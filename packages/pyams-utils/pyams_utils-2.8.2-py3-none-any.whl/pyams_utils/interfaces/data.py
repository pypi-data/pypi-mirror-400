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

"""PyAMS_utils data interface

This interface allows to define custom "data" properties on any object providing
IObjectData interface. These properties are used to render "data" attributes into
HTML code.
"""

from zope.interface import Interface
from zope.schema import Dict

__docformat__ = 'restructuredtext'


class IObjectData(Interface):
    """Object data generic interface

    Objects providing this interface can create an 'object_data' dictionary attribute which
    will be used to create matching HTML data attributes.
    """

    object_data = Dict(title="Data associated with this object",
                       required=False)


class IObjectDataRenderer(Interface):
    """Object data rendering interface"""

    def get_object_data(self):
        """Get object data as JSON string"""
