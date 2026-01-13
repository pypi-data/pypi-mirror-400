#
# Copyright (c) 2008-2018 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.factory module

This module provides a decorator and a small set of functions to handle object factories.
"""

import logging

import venusian
from zope.component import adapter, queryAdapter
from zope.interface import Interface, classImplements, implementer
from zope.interface.interface import InterfaceClass

from pyams_utils.interfaces import IObjectFactory
from pyams_utils.registry import get_current_registry


__docformat__ = 'restructuredtext'


LOGGER = logging.getLogger('PyAMS (utils)')


def is_interface(obj):
    """Check if given object is an interface"""
    return issubclass(obj.__class__, InterfaceClass)


def get_interface_name(iface):
    """Get interface full name"""
    return iface.__module__ + '.' + iface.__name__


def get_interface_base_name(iface):
    """Get interface base name"""
    return iface.__name__


@adapter(Interface)
@implementer(IObjectFactory)
class ObjectFactoryAdapter:
    """Most basic object factory adapter"""

    factory = None

    def __init__(self, context):
        self.context = context

    def __call__(self, *args, **kwargs):
        return self.factory(*args, **kwargs)  # pylint: disable=not-callable


_factories = {}
"""Mapping of registered factories"""


def register_factory(interface, klass, registry=None, name=''):
    """Register factory for a given interface

    :param interface: the interface for which the factory is registered
    :param klass: the object factory
    :param registry: the registry into which factory adapter should be registered; if None, the
        global registry is used
    :param name: custom name given to registered factory
    """

    class Temp(ObjectFactoryAdapter):
        """Object factory matching given interface"""
        classImplements(klass, interface)
        factory = klass

    if_name = get_interface_name(interface)
    if name:
        if_name = f'{if_name}::{name}'
    if registry is None:
        registry = get_current_registry()
    registry.registerAdapter(Temp, name=if_name)
    _factories.setdefault(interface, []).append((name, Temp))


class factory_config:  # pylint: disable=invalid-name,no-member
    """Class decorator to declare a default object factory"""

    venusian = venusian

    def __init__(self, provided, **settings):
        settings['provided'] = provided
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        depth = settings.pop('_depth', 0)

        def callback(context, name, obj):
            factory_name = settings.get('name', '')
            provided = settings.get('provides') or settings.get('provided')
            if not provided:
                raise TypeError("No provided interface(s) was given for registered factory %r" %
                                obj)
            if not isinstance(provided, tuple):
                provided = (provided,)

            config = context.config.with_package(info.module)  # pylint: disable=no-member
            for interface in provided:
                if name:
                    LOGGER.debug("Registering factory %s for interface %s with name %s",
                                 str(obj), str(interface), factory_name)
                else:
                    LOGGER.debug("Registering default factory %s for interface %s",
                                 str(obj), str(interface))
                register_factory(interface, obj, config.registry, factory_name)

        info = self.venusian.attach(wrapped, callback, category='pyramid',
                                    depth=depth + 1)
        if info.scope == 'class':  # pylint: disable=no-member
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings.get('attr') is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo  # pylint: disable=no-member
        return wrapped


def get_object_factory(interface, name=''):
    """Get registered factory for given interface

    :param interface: the interface for which a factory is requested
    :param name: name of requested factory
    :return: the requested object factory, or None if it can't be found
    """
    if not is_interface(interface):
        return interface
    if_name = get_interface_name(interface)
    if name:
        if_name = f'{if_name}::{name}'
    return queryAdapter(interface, IObjectFactory, name=if_name)


def get_all_factories(interface):
    """Get all registered factories for given interface

    :param interface: the interface for which factories are requested
    :return: an iterator over registered factories, containing tuples
        with name and factory class
    """
    for name, factory in _factories.get(interface, ()):
        yield name, factory.factory


def create_object(interface, name='', **kwargs):
    """Create an object for a given interface for which a factory has been registered

    :param interface: the interface for which a factory is requested
    :param name: name of requested factory
    :param kwargs: optional keywords arguments
    :return: an object implementing the provided interface, or None if no factory was registered
      for this interface
    """
    if is_interface(interface):
        factory = get_object_factory(interface, name)
    else:
        factory = interface
    if factory is None:
        return None
    return factory(**kwargs)
