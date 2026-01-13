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

"""PyAMS_utils.inherit module

This module is used to manage a generic inheritance between a content and
it's parent container. It also defines a custom InheritedFieldProperty which
allows to automatically manage inherited properties.
"""

from zope.interface import Interface, implementer
from zope.location import Location
from zope.schema.fieldproperty import FieldProperty

from pyams_utils.interfaces.inherit import IInheritInfo
from pyams_utils.traversing import get_parent
from pyams_utils.zodb import volatile_property


__docformat__ = 'restructuredtext'


@implementer(IInheritInfo)
class BaseInheritInfo(Location):
    """Base inherit class

    Subclasses may generally override target_interface and adapted_interface to
    correctly handle inheritance (see example in doctests).
    Please note also that adapters to this interface must correctly 'locate'
    """

    target_interface = Interface
    adapted_interface = Interface

    _inherit = FieldProperty(IInheritInfo['inherit'])

    @volatile_property
    def parent(self):
        """Get current parent"""
        return get_parent(self.__parent__, self.target_interface, allow_context=False)

    @property
    def can_inherit(self):
        """Check if inheritance is possible"""
        return self.target_interface.providedBy(self.parent)

    @property
    def inherit(self):
        """Check if inheritance is possible and activated"""
        return self._inherit if self.can_inherit else False

    @inherit.setter
    def inherit(self, value):
        """Activate inheritance"""
        if self.can_inherit:
            self._inherit = value
        del self.parent

    @property
    def no_inherit(self):
        """Inverted boolean value to check if inheritance is possible and activated"""
        return not bool(self.inherit)

    @no_inherit.setter
    def no_inherit(self, value):
        """Inverted inheritance setter"""
        self.inherit = not bool(value)

    @property
    def inherit_from(self):
        """Get current parent from which we inherit"""
        if not self.inherit:
            return self.__parent__
        parent = self.parent
        while self.adapted_interface(parent).inherit:
            parent = parent.parent  # pylint: disable=no-member
        return parent


class InheritedFieldProperty:
    """Inherited field property"""

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field  # pylint: disable=unused-private-member
        self.__name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self
        inherit_info = IInheritInfo(inst)
        if inherit_info.inherit and (inherit_info.parent is not None):
            # pylint: disable=not-callable
            return getattr(inherit_info.adapted_interface(inherit_info.parent), self.__name)
        return getattr(inst, f'_{self.__name}')

    def __set__(self, inst, value):
        inherit_info = IInheritInfo(inst)
        if not (inherit_info.can_inherit and inherit_info.inherit):
            setattr(inst, f'_{self.__name}', value)
