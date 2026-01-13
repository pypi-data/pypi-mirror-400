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

"""PyAMS_utils.size module

This module provides a small function which can be used to convert
a "size" value, given in bytes, to it's "human" representation.
"""

from babel import UnknownLocaleError
from babel.core import Locale
from babel.numbers import format_decimal

from pyams_utils.request import check_request


__docformat__ = 'restructuredtext'

from pyams_utils import _


def get_human_size(value, request=None):
    """Convert given bytes value in human readable format
    """
    if request is None:
        request = check_request()
    translate = request.localizer.translate
    try:
        locale = Locale(request.locale_name)
    except UnknownLocaleError:
        locale = Locale(request.registry.settings.get('pyramid.default_locale_name', 'en'))
    if value < 1024:
        return format_decimal(value, translate(_('0 bytes')), locale)
    value /= 1024
    if value < 1024:
        return format_decimal(value, translate(_('0.# Kb')), locale)
    value /= 1024
    if value < 1024:
        return format_decimal(value, translate(_('0.0# Mb')), locale)
    value /= 1024
    return format_decimal(value, translate(_('0.0## Gb')), locale)
