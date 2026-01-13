#
# Copyright (c) 2008-2015 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.registry module

This package is used to manage a *local registry*. A local registry is a *site management* component
created automatically on application startup by PyAMS_utils package. It can be used to store and
register components, mainly persistent utilities which are created and configured dynamically by a
site administrator; this can include SQLAlchemy engines, ZEO connections, and several PyAMS
utilities like security manager, medias converter, tasks scheduler and many other ones.

See :ref:`zca` to get a brief introduction about using a local registry with PyAMS packages.
"""

import logging
import threading
from inspect import isclass

import venusian
from ZODB.POSException import POSError
from pyramid.events import subscriber
from pyramid.interfaces import INewRequest
from pyramid.threadlocal import get_current_registry as get_pyramid_registry, manager
from zope.component.interfaces import ISite
from zope.interface import classImplements, implementedBy, providedBy
from zope.interface.interfaces import ComponentLookupError
from zope.traversing.interfaces import IBeforeTraverseEvent


__docformat__ = 'restructuredtext'

LOGGER = logging.getLogger('PyAMS (utils)')


class LocalRegistry(threading.local):
    """Local registry

    The local registry is defined to allow access to persistent utility
    registered and stored into ZODB.
    """

    _registry = None

    def get_registry(self):
        """Return local registry"""
        return self._registry

    def set_registry(self, registry):
        """Define local registry"""
        if ISite.providedBy(registry):
            registry = registry.getSiteManager()
        self._registry = registry


local_registry = LocalRegistry()  # pylint: disable=invalid-name


def get_local_registry():
    """Get local registry

    Local registry is automatically defined while traversing a site manager.
    """
    return local_registry.get_registry()


def set_local_registry(registry):
    """Define local registry"""
    local_registry.set_registry(registry)


def get_current_registry():
    """Get current or global registry

    The function is looking for given request registry.
    If registry is None, returns the global registry.
    """
    return get_pyramid_registry()


def get_registries():
    """Iterator on components registries

    Returns an iterator on current local registry (if any) and registries associated
    in current thread stack.
    """
    seen = []
    append = seen.append
    registry = local_registry.get_registry()
    if registry is not None:
        yield registry
        append(registry)
    for entry in reversed(manager.stack):
        stack_registry = entry.get('registry')
        if (stack_registry is not None) and (stack_registry not in seen):
            yield stack_registry
            append(stack_registry)


def registered_utilities():
    """Get utilities registrations as generator

    Iterates over utilities defined in all registries, starting with local ones.
    """
    for registry in get_registries():
        yield from registry.registeredUtilities()


def query_utility(provided, name='', default=None):
    """Query utility registered with given interface

    Do a registry lookup for given utility into local registry first, then on each registry
    associated with current thread stack.

    :param Interface provided: the requested interface
    :param str name: name of the requested utility
    :param object default: the default object returned if the requested utility can't be found
    :return: object; the requested object, or *default* if it can't be found
    """
    try:
        for registry in get_registries():
            utility = registry.queryUtility(provided, name, default)
            if utility is not None:
                return utility
    except POSError:
        pass
    return default


def get_utility(provided, name=''):
    """Get utility registered with given interface

    Do a registry lookup for given utility into local registry first, then on each registry
    associated with current thread stack.

    :param Interface provided: the requested interface
    :param str name: name of the requested utility
    :return: object; the requested object. A *ComponentLookupError* is raised if the utility
        can't be found.
    """
    for registry in get_registries():
        utility = registry.queryUtility(provided, name)
        if utility is not None:
            return utility
    raise ComponentLookupError(provided, name)


def get_utilities_for(interface):
    """Get utilities registered with given interface as (name, util) tuples iterator

    Do a registry lookup for matching utilities into local registry first, then on each registry
    associated with current thread stack.
    """
    for registry in get_registries():
        for utility in registry.getUtilitiesFor(interface):
            yield utility


def get_all_utilities_registered_for(interface):  # pylint: disable=invalid-name
    """Get list of registered utilities for given interface

    Do a registry lookup for matching utilities into local registry first, then on each registry
    associated with current thread stack.
    """
    result = []
    for registry in get_registries():
        for utilities in registry.getAllUtilitiesRegisteredFor(interface):
            result.append(utilities)
    return result


class utility_config:  # pylint: disable=invalid-name
    """Function or class decorator to register a utility in the global registry

    :param str name: default=''; name under which the utility is registered
    :param Interface provides: the interface for which the utility is registered

    Please note that a single utility can be registered several times (using several annotations),
    with different names.

    If several utilities are registered for the same interface with the same name, the last
    registered utility will override the previous ones.
    """

    venusian = venusian

    def __init__(self, **settings):
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        depth = settings.pop('_depth', 0)

        def callback(context, name, obj):  # pylint: disable=unused-argument
            if isinstance(obj, type):
                factory = obj
                component = None
            else:
                factory = None
                component = obj

            provided = settings.get('provides') or settings.get('provided')
            if provided is None:
                if factory:
                    provided = list(implementedBy(factory))
                else:
                    provided = list(providedBy(component))
                if len(provided) == 1:
                    provided = provided[0]
                else:
                    raise TypeError("Missing 'provides' argument")
            if isclass(obj) and not provided.implementedBy(obj):
                classImplements(obj, provided)

            LOGGER.debug(f"Registering utility {str(component) if component else str(factory)} "
                         f"named '{settings.get('name', '')}' "
                         f"providing {str(provided)}")
            registry = settings.get('registry')
            if registry is None:
                config = context.config.with_package(info.module)  # pylint: disable=no-member
                registry = config.registry
            registry.registerUtility(component=component, factory=factory,
                                     provided=provided, name=settings.get('name', ''))

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


#
# Request registry management
#

@subscriber(INewRequest)
def handle_new_request(event):  # pylint: disable=unused-argument
    """New request event subscriber

    Is used to initialize local registry to None for any new request
    """
    set_local_registry(None)


@subscriber(IBeforeTraverseEvent, context_selector=ISite)
def handle_site_before_traverse(event):
    """Before traverse event subscriber

    Define site's local registry when an object implementing ISite is traversed
    """
    set_local_registry(event.object.getSiteManager())
