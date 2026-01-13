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

"""PyAMS_utils.interfaces.intids module

Small set of interfaces used by IIntIds utilities.
"""

from zope.interface import Interface
from zope.schema import Int, TextLine


__docformat__ = 'restructuredtext'

from pyams_utils import _


#
# Generic interfaces
#

class IIndexLength(Interface):
    """Index length interface"""

    count = Int(title=_("Indexed elements count"),
                readonly=True)


class IUniqueID(Interface):
    """Interface used to get unique ID of an object"""

    oid = TextLine(title="Unique ID",
                   description="Globally unique identifier of this object can be used to create "
                               "internal links",
                   readonly=True)
