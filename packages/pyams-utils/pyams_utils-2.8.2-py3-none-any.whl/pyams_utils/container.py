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
# pylint: disable=no-name-in-module

"""PyAMS_utils.container module

This module provides several classes, adapters and functions about containers.
"""

from typing import Iterable

from BTrees.OOBTree import OOBTree  # pylint: disable=import-error
from ZODB.interfaces import IConnection
from persistent.interfaces import IPersistent
from persistent.list import PersistentList
from pyramid.threadlocal import get_current_registry
from zope.container.interfaces import IContainer
from zope.container.ordered import OrderedContainer
from zope.interface import Interface
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from zope.location import locate
from zope.location.interfaces import IContained, ISublocations

try:
    from pyams_catalog.utils import index_object
except ImportError:
    index_object = None

from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.interfaces import ICacheKeyValue


__docformat__ = 'restructuredtext'


class SimpleContainerMixin:
    """Simple container mixin class"""

    def append(self, item: IPersistent, notify=True):
        """Append object to container"""
        try:
            IConnection(self).add(item)
        except TypeError:
            pass
        key = ICacheKeyValue(item)
        if not notify:
            # pre-locate container item to avoid multiple notifications
            locate(item, self, key)
        self[key] = item
        if (not notify) and (index_object is not None):
            # make sure that gallery item is correctly indexed
            index_object(item)
        return item.__name__


class BTreeOrderedContainer(SimpleContainerMixin, OrderedContainer):
    """BTree based ordered container

    This container maintain a manual order of it's contents
    """

    def __init__(self):
        # pylint: disable=super-init-not-called
        self._data = OOBTree()
        self._order = PersistentList()


class ParentSelector:
    """Interface based parent selector

    This selector can be used as a subscriber predicate on IObjectAddedEvent to define
    an interface that the new parent must support for the event to be applied:

    .. code-block:: python

        from pyams_utils.interfaces.site import ISiteRoot

        @subscriber(IObjectAddedEvent, parent_selector=ISiteRoot)
        def siteroot_object_added_event_handler(event):
            '''This is an event handler for an ISiteRoot object added event'''
    """

    def __init__(self, interfaces: Iterable[Interface], config):  # pylint: disable=unused-argument
        if not isinstance(interfaces, (list, tuple, set)):
            interfaces = (interfaces,)
        self.interfaces = interfaces

    def text(self):
        """Predicate string output"""
        return 'parent_selector = %s' % str(self.interfaces)

    phash = text

    def __call__(self, event: IObjectMovedEvent):
        if not IObjectMovedEvent.providedBy(event):  # pylint: disable=no-value-for-parameter
            return False
        for intf in self.interfaces:
            try:
                if intf.providedBy(event.newParent):
                    return True
            except (AttributeError, TypeError):
                if isinstance(event.newParent, intf):
                    return True
        return False


@adapter_config(required=IContained,
                provides=ISublocations)
class ContainerSublocationsAdapter(ContextAdapter):
    """Contained object sub-locations adapter

    This adapter checks for custom ISublocations interface adapters which can
    be defined by any component to get access to inner locations, defined for
    example via annotations.
    """

    def sublocations(self):
        """See `zope.location.interfaces.ISublocations` interface"""
        context = self.context
        # Check for adapted sub-locations first...
        registry = get_current_registry()
        for name, adapter in registry.getAdapters((context,), ISublocations):
            if not name:  # don't reuse default adapter!!
                continue
            yield from adapter.sublocations()
        # then yield container items
        if IContainer.providedBy(context):
            yield from context.values()
