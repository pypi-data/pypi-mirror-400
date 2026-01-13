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

"""PyAMS_utils.interfaces.traversing module

The IPathElements is used by an Hypatia index to store internal IDs of parents of a given
objects; this allows to query catalog for objects which are located "inside" a given parent
object, identified by it's internal ID.
"""

from zope.interface import Interface
from zope.schema import Int, List


__docformat__ = 'restructuredtext'


class IPathElements(Interface):
    """Path elements interface"""

    parents = List(title="Element parents",
                   description="Internal IDs of parents objects",
                   value_type=Int())
