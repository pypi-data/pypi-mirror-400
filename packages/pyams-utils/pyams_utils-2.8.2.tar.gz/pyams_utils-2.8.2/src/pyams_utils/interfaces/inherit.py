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

"""PyAMS_utils.interfaces.inherit module

This module defines interfaces which are used by the :py:mod:`inherit <pyams_utils.inherit>`
module
"""

from pyramid.interfaces import ILocation

from zope.interface import Attribute
from zope.schema import Bool


__docformat__ = 'restructuredtext'

from pyams_utils import _


class IInheritInfo(ILocation):
    """Inheritance info"""

    target_interface = Attribute("Parent target interface")
    adapted_interface = Attribute("Context or parent adapted interface")

    parent = Attribute("First parent supporting target interface")

    can_inherit = Attribute("Can inherit from parent?")

    inherit = Bool(title=_("Inherit from parent"),
                   required=False,
                   default=True)

    no_inherit = Bool(title=_("Don't inherit from parent"),
                      required=False,
                      default=False)

    inherit_from = Attribute("Parent from which adapted interface is inherited")
