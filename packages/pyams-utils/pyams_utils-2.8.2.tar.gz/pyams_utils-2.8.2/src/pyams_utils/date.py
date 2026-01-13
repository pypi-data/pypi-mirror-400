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

"""PyAMS_utils.date module

This module provides several functions concerning conversion, parsing and formatting of
dates and datetimes.
"""

from datetime import date, datetime, time, timedelta, timezone

from pyramid.interfaces import IRequest
from zope.dublincore.interfaces import IZopeDublinCore
from zope.interface import Interface

from pyams_utils.adapter import ContextRequestAdapter, ContextRequestViewAdapter, \
    adapter_config
from pyams_utils.interfaces import MISSING_INFO
from pyams_utils.interfaces.tales import ITALESExtension
from pyams_utils.interfaces.text import ITextRenderer
from pyams_utils.request import check_request
from pyams_utils.timezone import UTC, gmtime, tztime


__docformat__ = 'restructuredtext'

from pyams_utils import _


def unidate(value):
    """Get specified date converted to unicode ISO format

    Dates are always assumed to be stored in UTC

    :param date value: input date to convert to unicode
    :return: unicode; input date converted to unicode

    >>> from datetime import datetime
    >>> from pyams_utils.date import unidate
    >>> value = datetime(2016, 11, 15, 10, 13, 12)
    >>> unidate(value)
    '2016-11-15T10:13:12+00:00'
    >>> unidate(None) is None
    True
    """
    if value is not None:
        value = gmtime(value)
        return value.isoformat('T')
    return None


def parse_date(value, to_gmt=True):
    """Get date specified in unicode ISO format to Python datetime object

    Dates are always assumed to be stored in UTC

    :param str value: unicode date to be parsed
    :param bool to_gmt: if True, date is converted to UTC timezone; otherwise, date is
        left in its initial timezone
    :return: datetime; the specified value, converted to datetime

    >>> from pyams_utils.date import parse_date
    >>> parse_date('2016-11-15T10:13:12+00:00')
    datetime.datetime(2016, 11, 15, 10, 13, 12, tzinfo=<UTC>)
    >>> parse_date('2016-11-15T10:13:12+02:00', to_gmt=False)
    datetime.datetime(2016, 11, 15, 10, 13, 12, tzinfo=...)
    >>> parse_date(None) is None
    True
    """
    if value is not None:
        value = datetime.fromisoformat(value)
        if to_gmt:
            value = gmtime(value)
        return value
    return None


def parse_time(value):
    """Get time specified in unicode ISO format to Python time object

    Times are always assumed to be stored without timezone

    :param str value: unicode time to be parsed
    :return: time; the specified value, converted to time

    >>> from pyams_utils.date import parse_time
    >>> parse_time('2016-11-15T10:13:12+00:00')
    datetime.time(10, 13, 12)
    >>> parse_time('10:13')
    datetime.time(10, 13)
    >>> parse_time(None) is None
    True
    """
    if value is not None:
        try:
            return time.fromisoformat(value)
        except ValueError:
            return datetime.fromisoformat(value).time()
    return None


def date_to_datetime(value):
    """Get datetime value converted from a date or datetime object

    :param date/datetime value: a date or datetime value to convert
    :return: datetime; input value converted to datetime

    >>> from datetime import date, datetime
    >>> from pyams_utils.date import date_to_datetime
    >>> value = date(2016, 11, 15)
    >>> date_to_datetime(value)
    datetime.datetime(2016, 11, 15, 0, 0)
    >>> value = datetime(2016, 11, 15, 10, 13, 12)
    >>> value
    datetime.datetime(2016, 11, 15, 10, 13, 12)
    >>> date_to_datetime(value) is value
    True
    >>> date_to_datetime(None) is None
    True
    """
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime(value.year, value.month, value.day)


@adapter_config(name='isoformat',
                context=(Interface, Interface, Interface),
                provides=ITALESExtension)
class ISOFormatTalesAdapter(ContextRequestViewAdapter):
    """tales:isoformat(context) TALES adapter

    A PyAMS TALES extension to get provided date or datetime in ISO format
    """

    def render(self, context=None):
        """Render TALES extension"""
        if context is None:
            context = self.request.context
        datetime = date_to_datetime(context)
        return datetime.isoformat()


SH_DATE_FORMAT = _("%d/%m/%Y")
SH_TIME_FORMAT = _("%H:%M")
SH_DATETIME_FORMAT = _("%d/%m/%Y - %H:%M")

EXT_DATE_FORMAT = _("on %d/%m/%Y")
EXT_TIME_FORMAT = _("at %H:%M")
EXT_DATETIME_FORMAT = _("on %d/%m/%Y at %H:%M")


def format_date(value, format_string=EXT_DATE_FORMAT, request=None):
    """Format given date with the given format

    :param datetime value: the value to format
    :param str format_string: a format string to use by `strftime` function
    :param request: the request from which to extract localization info for translation
    :return: str; input datetime converted to given format

    >>> from datetime import datetime
    >>> from pyams_utils.date import format_date, SH_DATE_FORMAT
    >>> value = datetime(2016, 11, 15, 10, 13, 12)
    >>> format_date(value)
    'on 15/11/2016'
    >>> format_date(value, SH_DATE_FORMAT)
    '15/11/2016'
    >>> format_date(None)
    '--'
    """
    if not value:
        return MISSING_INFO
    if request is None:
        request = check_request()
    localizer = request.localizer
    return datetime.strftime(tztime(value), localizer.translate(format_string))


@adapter_config(name='format_date',
                context=(Interface, Interface, Interface),
                provides=ITALESExtension)
class DateTalesAdapter(ContextRequestViewAdapter):
    """Date formatter TALES extension"""

    def render(self, context=None, put_prefix=True, format_string=SH_DATE_FORMAT):
        if context is None:
            dc = IZopeDublinCore(self.context, None)
            if dc is not None:
                context = dc.modified
        if put_prefix:
            return format_date(context, request=self.request)
        return format_date(context, format_string=format_string, request=self.request)


def format_time(value, format_string=EXT_TIME_FORMAT, request=None):
    """Format given datetime with given format string"""
    if not value:
        return MISSING_INFO
    if request is None:
        request = check_request()
    localizer = request.localizer
    return time.strftime(tztime(value).time(), localizer.translate(format_string))


@adapter_config(name='format_time',
                context=(Interface, Interface, Interface),
                provides=ITALESExtension)
class TimeTalesAdapter(ContextRequestViewAdapter):
    """Time formatter TALES extension"""

    def render(self, context=None, put_prefix=True, format_string=SH_TIME_FORMAT):
        if context is None:
            dc = IZopeDublinCore(self.context, None)
            if dc is not None:
                context = dc.modified
        if put_prefix:
            return format_time(context, request=self.request)
        return format_time(context, format_string=format_string, request=self.request)


def format_datetime(value, format_string=EXT_DATETIME_FORMAT, request=None):
    """Format given datetime with the given format including time

    :param datetime value: the value to format
    :param str format_string: a format string to use by `strftime` function
    :param request: request; the request from which to extract localization info for translation
    :return: str; input datetime converted to given format

    >>> from datetime import datetime
    >>> from pyams_utils.date import format_datetime, SH_DATETIME_FORMAT
    >>> value = datetime(2016, 11, 15, 10, 13, 12)
    >>> format_datetime(value)
    'on 15/11/2016 at 10:13'
    >>> format_datetime(value, SH_DATETIME_FORMAT)
    '15/11/2016 - 10:13'
    >>> format_datetime(None)
    '--'
    """
    return format_date(value, format_string, request)


@adapter_config(name='format_datetime',
                context=(Interface, Interface, Interface),
                provides=ITALESExtension)
class DatetimeTalesAdapter(ContextRequestViewAdapter):
    """Datetime format TALES extension"""

    def render(self, context=None, put_prefix=True, format_string=SH_DATETIME_FORMAT):
        if context is None:
            dc = IZopeDublinCore(self.context, None)
            if dc is not None:
                context = dc.modified
        if put_prefix:
            return format_datetime(context, request=self.request)
        return format_datetime(context, format_string=format_string, request=self.request)


def get_age(value, request=None):
    """Get 'human' age of a given datetime (including timezone) compared to current datetime
    (in UTC)

    :param datetime value: input datetime to be compared with current datetime
    :return: str; the delta value, converted to months, weeks, days, hours or minutes

    >>> from datetime import datetime, timedelta, timezone
    >>> from pyams_utils.date import get_age
    >>> now = datetime.now(timezone.utc)
    >>> get_age(now)
    'less than 5 minutes ago'
    >>> get_age(now - timedelta(minutes=10))
    '10 minutes ago'
    >>> get_age(now - timedelta(hours=2))
    '2 hours ago'
    >>> get_age(now - timedelta(days=1))
    'yesterday'
    >>> get_age(now - timedelta(days=2))
    'the day before yesterday'
    >>> get_age(now - timedelta(days=4))
    '4 days ago'
    >>> get_age(now - timedelta(weeks=2))
    '2 weeks ago'
    >>> get_age(now - timedelta(days=80))
    '3 months ago'
    >>> get_age(None)
    '--'
    """
    if not value:
        return MISSING_INFO
    if request is None:
        request = check_request()
    translate = request.localizer.translate
    now = gmtime(datetime.now(timezone.utc))
    delta = now - gmtime(value)
    if delta.days > 60:
        return translate(_("%d months ago")) % int(round(delta.days * 1.0 / 30))
    if delta.days > 10:
        return translate(_("%d weeks ago")) % int(round(delta.days * 1.0 / 7))
    if delta.days > 2:
        return translate(_("%d days ago")) % delta.days
    if delta.days == 2:
        return translate(_("the day before yesterday"))
    if delta.days == 1:
        return translate(_("yesterday"))
    hours = int(round(delta.seconds * 1.0 / 3600))
    if hours > 1:
        return translate(_("%d hours ago")) % hours
    if delta.seconds > 300:
        return translate(_("%d minutes ago")) % int(round(delta.seconds * 1.0 / 60))
    return translate(_("less than 5 minutes ago"))


def get_duration(first, last=None, request=None):  # pylint: disable=too-many-branches
    """Get 'human' delta as string between two dates

    :param datetime|timedelta first: start date
    :param datetime last: end date, or current date (in UTC) if None
    :param request: the request from which to extract localization infos
    :return: str; approximate delta between the two input dates

    >>> from datetime import datetime, timedelta, timezone
    >>> from pyams_utils.date import get_duration
    >>> from pyams_utils.timezone import UTC
    >>> from pyramid.testing import DummyRequest

    Let's try with a provided timedelta:

    >>> duration = timedelta(seconds=20)
    >>> get_duration(duration)
    '20 seconds'

    >>> date1 = datetime(2015, 1, 1)
    >>> date2 = datetime(2014, 3, 1)
    >>> get_duration(date1, date2)
    '10 months'

    Dates order is not important:

    >>> get_duration(date2, date1)
    '10 months'
    >>> date2 = datetime(2014, 11, 10)
    >>> get_duration(date1, date2)
    '7 weeks'
    >>> date2 = datetime(2014, 12, 26)

    Let's try with a requuest:

    >>> request = DummyRequest()
    >>> get_duration(date1, date2, request)
    '6 days'

    For durations lower than 2 days, duration also display hours:

    >>> date1 = datetime(2015, 1, 1)
    >>> date2 = datetime(2015, 1, 2, 15, 10, 0)
    >>> get_duration(date1, date2, request)
    '1 day and 15 hours'
    >>> date2 = datetime(2015, 1, 2)
    >>> get_duration(date1, date2, request)
    '24 hours'
    >>> date2 = datetime(2015, 1, 1, 13, 12)
    >>> get_duration(date1, date2, request)
    '13 hours'
    >>> date2 = datetime(2015, 1, 1, 1, 15)
    >>> get_duration(date1, date2, request)
    '75 minutes'
    >>> date2 = datetime(2015, 1, 1, 0, 0, 15)
    >>> get_duration(date1, date2, request)
    '15 seconds'
    >>> now = datetime.now(timezone.utc)
    >>> delta = now - UTC.localize(date1)
    >>> get_duration(date1, None, request) == '%d months' % int(round(delta.days * 1.0 / 30))
    True
    """
    if isinstance(first, timedelta):
        delta = first
    else:
        if last is None:
            last = datetime.now(timezone.utc)
        assert isinstance(first, datetime) and isinstance(last, datetime)
        if not first.tzinfo:
            first = UTC.localize(first)
        if not last.tzinfo:
            last = UTC.localize(last)
        first, last = min(first, last), max(first, last)
        delta = last - first
    if request is None:
        request = check_request()
    translate = request.localizer.translate
    if delta.days > 60:
        return translate(_("%d months")) % int(round(delta.days * 1.0 / 30))
    if delta.days > 10:
        return translate(_("%d weeks")) % int(round(delta.days * 1.0 / 7))
    if delta.days >= 2:
        return translate(_("%d days")) % delta.days
    hours = int(round(delta.seconds * 1.0 / 3600))
    if delta.days == 1:
        if hours == 0:
            return translate(_("24 hours"))
        return translate(_("%d day and %d hours")) % (delta.days, hours)
    if hours > 2:
        return translate(_("%d hours")) % hours
    minutes = int(round(delta.seconds * 1.0 / 60))
    if minutes > 2:
        return translate(_("%d minutes")) % minutes
    return translate(_("%d seconds")) % delta.seconds


#
# Timestamp TALES extension
#

TS_FORMATTERS = {
    'iso': datetime.isoformat,
    'isodate': date.isoformat,
    'datetime': date_to_datetime
}


def get_timestamp(context, formatting=None):
    """Get timestamp matching context modification date"""
    format_func = TS_FORMATTERS.get(formatting, datetime.timestamp)
    zdc = IZopeDublinCore(context, None)
    if zdc is not None:
        return format_func(tztime(zdc.modified))
    return format_func(tztime(datetime.now(timezone.utc)))


@adapter_config(name='timestamp',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class TimestampTalesAdapter(ContextRequestViewAdapter):
    """extension:timestamp(context) TALES adapter

    A PyAMS TALES extension to get timestamp based on last context modification date.
    """

    def render(self, context=None, formatting=None):
        """Render TALES extension"""
        if context is None:
            context = self.request.context
        return get_timestamp(context, formatting)


#
# 'now' text renderer
#

@adapter_config(name='now',
                required=(str, IRequest),
                provides=ITextRenderer)
class NowTextRenderer(ContextRequestAdapter):
    """Text renderer for current server datetime"""

    @staticmethod
    def render(format_string=None, **kwargs):
        """Render current server datetime using provided format string"""
        if not format_string:
            format_string = '%c'
        now = tztime(datetime.now(timezone.utc))
        return now.strftime(format_string)
