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

"""Adapters management package

This package provides a small set of standard base adapters for *context*, *context* and *request*,
and *context* and *request* and *view*.

See :ref:`zca` to see how PyAMS can help components management.
"""

import logging
from inspect import isclass

import venusian
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides, classImplements, implementedBy
from zope.lifecycleevent import ObjectCreatedEvent
from zope.location import locate as zope_locate

from pyams_utils.factory import get_object_factory, is_interface
from pyams_utils.registry import get_current_registry


__docformat__ = 'restructuredtext'


LOGGER = logging.getLogger('PyAMS (utils)')


class ContextAdapter:
    """Context adapter"""

    def __init__(self, context):
        self.context = context


class ContextRequestAdapter:
    """Context + request multi-adapter"""

    def __init__(self, context, request):
        self.context = context
        self.request = request


class ContextRequestViewAdapter:
    """Context + request + view multi-adapter"""

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view


class NullAdapter:
    """An adapter which always return None!

    Can be useful to override a default adapter...
    """

    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        return None


class adapter_config:    # pylint: disable=invalid-name
    """Function or class decorator to declare an adapter

    Annotation parameters can be:

    :param str='' name: name of the adapter
    :param [Interface...] required: an interface, or a tuple of interfaces, that the component
        adapts; 'adapts' and 'context' are deprecated synonyms for 'required' argument name
    :param Interface provided: the interface that the adapter provides; 'provides' is a synonym
        for 'provided' argument name
    :param boolean force_implements: if True (the default), the registered adapter class will
        automatically implement the *provided* interface; otherwise, the implementation is not
        forced
    :param registry: the registry into which adapter registration should be made
    """

    venusian = venusian

    def __init__(self, **settings):
        if 'for_' in settings:
            if settings.get('required') is None:
                settings['required'] = settings.pop('for_')
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        depth = settings.pop('_depth', 0)

        def callback(context, name, obj):  # pylint: disable=unused-argument
            required = settings.get('required') or settings.get('adapts') or settings.get('context')
            if required is None:
                required = getattr(obj, '__component_adapts__', None)
                if required is None:
                    raise TypeError("No for argument was provided for %r and "
                                    "can't determine what the factory adapts." % obj)
            if not isinstance(required, tuple):
                required = (required,)

            provided = settings.get('provides') or settings.get('provided')
            if provided is None:
                intfs = list(implementedBy(obj))
                if len(intfs) == 1:
                    provided = intfs[0]
                if provided is None:
                    raise TypeError("Missing 'provides' argument")
            if isclass(obj) and not provided.implementedBy(obj) and \
                    settings.get('force_implements', True):
                classImplements(obj, provided)

            LOGGER.debug("Registering adapter %s for %s providing %s",
                         str(obj), str(required), str(provided))
            registry = settings.get('registry')
            if registry is None:
                config = context.config.with_package(info.module)  # pylint: disable=no-member
                registry = config.registry
            registry.registerAdapter(obj, required, provided, settings.get('name', ''))

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


def query_adapter(interface, request, context=None, view=None, name=''):
    """Registry adapter lookup helper

    If view is provided, this function is trying to find a multi-adapter to given interface
    for request, context and view; if not found, the lookup is done for request and context,
    and finally only for context.

    :param interface: adapter provided interface
    :param request: current request
    :param context: current context; if context is None, request context is used
    :param view: current view
    :param name: adapter name
    """
    registry = request.registry
    if context is None:
        context = request.context
    adapter = registry.queryMultiAdapter((context, request, view), interface, name=name) \
        if view is not None else None
    if adapter is None:
        adapter = registry.queryMultiAdapter((context, request), interface, name=name)
    if adapter is None:
        adapter = registry.queryAdapter(context, interface, name=name)
    return adapter


def get_annotation_adapter(context, key, factory=None, markers=None, notify=True,
                           locate=True, parent=None, name=None, callback=None, **kwargs):
    # pylint: disable=too-many-arguments
    """Get an adapter via object's annotations, creating it if not existent

    :param object context: context object which should be adapted
    :param str key: annotations key to look for
    :param factory: if annotations key is not found, this is the factory which will be used to
        create a new object; factory can be a class or callable object, or an interface for which
        a factory has been registered; if factory is None and is requested object can't be found,
        None is returned
    :param markers: if not None, list of marker interfaces which created adapter should provide
    :param bool=True notify: if 'False', no notification event will be sent on object creation
    :param bool=True locate: if 'False', the new object is not attached to any parent
    :param object=None parent: parent to which new object is attached; if None, object is
        attached to context
    :param str=None name: if locate is not False, this is the name with which the new object is
        attached to it's parent
    :param callback: if not None, callback function which will be called after object creation
    """
    annotations = IAnnotations(context, None)
    if annotations is None:
        return None
    adapter = annotations.get(key)  # pylint: disable=assignment-from-no-return
    if adapter is None:
        if 'default' in kwargs:
            return kwargs['default']
        if factory is None:
            return None
        if is_interface(factory):
            factory = get_object_factory(factory)
            assert factory is not None, "Missing object factory"
        adapter = annotations[key] = factory()
        if adapter is not None:
            if markers:
                if not isinstance(markers, (list, tuple, set)):
                    markers = {markers}
                for marker in markers:
                    alsoProvides(adapter, marker)
            if notify:
                get_current_registry().notify(ObjectCreatedEvent(adapter))
            if locate:
                zope_locate(adapter, context if parent is None else parent, name)
                if getattr(context, '_p_jar', None) is not None:
                    context._p_jar.add(adapter)
            if callback:
                callback(adapter)
    return adapter


def get_adapter_weight(item):
    """Get adapters weight sort key"""
    name, adapter = item
    try:
        return int(adapter.weight), name
    except (TypeError, AttributeError):
        return 0, name
