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

"""PyAMS_utils.intids module

This module provides utility functions and helpers to help usage of IIntIds utilities.
Pyramid events subscribers are also declared to match Zope events with Pyramid IntIds related
events
"""

from persistent.interfaces import IPersistent
from pyramid.events import subscriber
from zope.intid import intIdEventNotify
from zope.intid.interfaces import IIntIdEvent, IIntIds, IntIdAddedEvent, IntIdRemovedEvent
from zope.keyreference.interfaces import IKeyReference, NotYet
from zope.lifecycleevent import ObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.location.interfaces import ISublocations

from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.interfaces.intids import IUniqueID
from pyams_utils.registry import get_all_utilities_registered_for, get_current_registry, \
    query_utility


__docformat__ = 'restructuredtext'


@adapter_config(required=IPersistent, provides=IUniqueID)
class UniqueIdAdapter(ContextAdapter):
    """Object unique ID adapter

    This adapter is based on a registered IIntIds utility to get a unique ID
    for any persistent object.
    """

    @property
    def oid(self):
        """Get context ID in hexadecimal form"""
        intids = query_utility(IIntIds)
        if intids is not None:
            object_id = intids.register(self.context)
            if object_id is not None:
                return hex(object_id)[2:]
        return None


def get_object_uid(obj):
    """Get object key name for given object"""
    unique_id = IUniqueID(obj, None)
    if unique_id is not None:
        return unique_id.oid
    return None


@subscriber(IObjectAddedEvent, context_selector=IPersistent)
def handle_added_object(event):
    """Notify IntId utility for added objects

    This subscriber is used for all persistent objects to be registered
    in all locally registered IIntIds utilities.
    """
    utilities = tuple(get_all_utilities_registered_for(IIntIds))
    if utilities:
        # assert that there are any utilities
        try:
            key = IKeyReference(event.object, None)
        except NotYet:
            pass
        else:
            # Register only objects that adapt to key reference
            if key is not None:
                idmap = {}
                for utility in utilities:
                    idmap[utility] = utility.register(key)
                # Notify the catalogs that this object was added.
                get_current_registry().notify(IntIdAddedEvent(event.object, event, idmap))


@subscriber(IObjectRemovedEvent, context_selector=IPersistent)
def handle_removed_object(event):
    """Notify IntId utility for removed objects

    This subscriber is used for all persistent objects to be unregistered
    from all locally registered IIntIds utilities.
    """
    registry = get_current_registry()
    locations = ISublocations(event.object, None)
    if locations is not None:
        for location in locations.sublocations():  # pylint: disable=too-many-function-args
            registry.notify(ObjectRemovedEvent(location))
    utilities = tuple(get_all_utilities_registered_for(IIntIds))
    if utilities:
        try:
            key = IKeyReference(event.object, None)
        except NotYet:
            pass
        else:
            # Register only objects that adapt to key reference
            if key is not None:
                # Notify the catalogs that this object is about to be removed.
                registry.notify(IntIdRemovedEvent(event.object, event))
                for utility in utilities:
                    try:
                        utility.unregister(key)
                    except KeyError:
                        pass


@subscriber(IIntIdEvent)
def handle_intid_event(event):
    """IntId event subscriber

    This event is used to dispatch all IIntIdEvent events using Pyramid events subscribers
    to matching subscribers using Zope events
    """
    intIdEventNotify(event)
