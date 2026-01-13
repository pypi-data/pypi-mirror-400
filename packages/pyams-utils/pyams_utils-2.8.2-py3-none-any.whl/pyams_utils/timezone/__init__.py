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

"""PyAMS_utils.timezone package

All datetime values should be stored in UTC to avoid any problem.
Then values can be displayed to users using a specific timezone; by default, used timezone
is the one specified into server settings via an IServerTimezone utility which is created
automatically when initializing a new site.

There is no easy way to get user's timezone from it's browser settings; so the more common
choice is to let users define their timezone in their profile's settings.
"""

from datetime import datetime

import pytz
from pyramid.interfaces import IRequest
from zope.interface.common.idatetime import ITZInfo

from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.timezone import IServerTimezone
from pyams_utils.registry import query_utility


__docformat__ = 'restructuredtext'


GMT = pytz.timezone('GMT')
UTC = pytz.timezone('UTC')


@adapter_config(required=IRequest, provides=ITZInfo)
def tzinfo(request=None):  # pylint: disable=unused-argument
    """request to timezone adapter

    There is no easy way to get timezone from a request.
    This adapter assumes that the timezone is given by
    a registered utility...
    """
    util = query_utility(IServerTimezone)
    if util is not None:
        return pytz.timezone(util.timezone)
    return UTC


def tztime(value):
    """Convert datetime to local timezone

    :param datetime value: input datetime; value is assumed to be in UTC if no timezone is given
    """
    if not value:
        return None
    if not isinstance(value, datetime):
        return value
    if not value.tzinfo:
        value = UTC.localize(value)
    return value.astimezone(tzinfo())


def gmtime(value):
    """Convert datetime to UTC

    Value is assumed to be in UTC if no timezone is given
    """
    if not value:
        return None
    if not isinstance(value, datetime):
        return value
    if not value.tzinfo:
        value = UTC.localize(value)
    return value.astimezone(UTC)


def localgmtime(value):
    """Convert datetime to UTC

    Value is assumed to be in server timezone if none is given
    """
    if not value:
        return None
    if not isinstance(value, datetime):
        return value
    if not value.tzinfo:
        value = tzinfo().localize(value)
    return value.astimezone(UTC)
