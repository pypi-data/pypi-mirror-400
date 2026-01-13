#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.interfaces module

This module defines generic constants and interfaces.
"""

from zope.interface import Interface
from zope.schema.interfaces import ConstraintNotSatisfied, InvalidDottedName, InvalidId, \
    InvalidURI, InvalidValue, NotAContainer, NotAnIterator, NotUnique, RequiredMissing, \
    SchemaNotFullyImplemented, SchemaNotProvided, TooBig, TooLong, TooShort, TooSmall, Unbound, \
    WrongContainedType, WrongType


__docformat__ = 'restructuredtext'

from pyams_utils import _


#
# Custom zope.schema exceptions messages
#

WrongContainedType.__doc__ = _("""Wrong contained type""")
NotUnique.__doc__ = _("""One or more entries of sequence are not unique.""")
SchemaNotFullyImplemented.__doc__ = _("""Schema not fully implemented""")
SchemaNotProvided.__doc__ = _("""Schema not provided""")
InvalidURI.__doc__ = _("""The specified URI is not valid.""")
InvalidId.__doc__ = _("""The specified id is not valid.""")
InvalidDottedName.__doc__ = _("""The specified dotted name is not valid.""")
Unbound.__doc__ = _("""The field is not bound.""")

RequiredMissing.__doc__ = _("""Required input is missing.""")
WrongType.__doc__ = _("""Object is of wrong type.""")
TooBig.__doc__ = _("""Value is too big""")
TooSmall.__doc__ = _("""Value is too small""")
TooLong.__doc__ = _("""Value is too long""")
TooShort.__doc__ = _("""Value is too short""")
InvalidValue.__doc__ = _("""Invalid value""")
ConstraintNotSatisfied.__doc__ = _("""Constraint not satisfied""")
NotAContainer.__doc__ = _("""Not a container""")
NotAnIterator.__doc__ = _("""Not an iterator""")


#
# Custom interfaces
#

TIMEZONES_VOCABULARY_NAME = 'pyams_utils.timezones'
ENCODINGS_VOCABULARY_NAME = 'pyams_utils.encodings'

ZODB_CONNECTIONS_VOCABULARY_NAME = 'pyams_utils.zodb.connections'
ZEO_CONNECTIONS_VOCABULARY_NAME = 'pyams_utils.zeo.connections'

DISPLAY_CONTEXT_KEY_NAME = 'pyams_utils.request.display_context'
"""Request annotations key name used to set display context"""


class MissingRequestError(Exception):
    """Error raised when no request is available"""


class IObjectFactory(Interface):
    """Object factory interface

    This interface can be used to register an "interface's object factory".
    For a given interface, such factory can be used to get an instance of an object providing
    this interface; several factories can be registered for the same interface if they have
    distinct names. See :py:mod:`pyams_utils.factory` module.
    """


class ICacheKeyValue(Interface):
    """Interface used to get string representation of a given object as cache key

    Several default adapters are given for objects (using their "id()"), strings (using string as
    key) and for persistent objects (using their persistent OID); you are free to provide your
    own adapters.
    """


class IOptionalUtility(Interface):
    """Marker interface for utilities that can be removed"""


MISSING_INFO = '--'
"""Default string used to display missing information"""
