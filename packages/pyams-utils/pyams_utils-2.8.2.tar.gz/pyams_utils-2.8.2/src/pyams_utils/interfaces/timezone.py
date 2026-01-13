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

"""PyAMS_utils.interfaces.timezone module

This module provides timezone utility interface and schema field
"""

from zope.interface import Interface

from pyams_utils.schema import TimezoneField


__docformat__ = 'restructuredtext'

from pyams_utils import _


class IServerTimezone(Interface):
    """Server timezone interface"""

    timezone = TimezoneField(title=_("Server timezone"),
                             description=_("Default server timezone"),
                             required=True)
