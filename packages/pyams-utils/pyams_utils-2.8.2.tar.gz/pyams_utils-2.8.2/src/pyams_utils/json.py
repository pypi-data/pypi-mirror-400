#
# Copyright (c) 2008-2018 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.json package

A small utility module which provides a default JSON encoder to automatically convert
dates and datetimes to ISO format

    >>> import json as stock_json
    >>> from datetime import datetime
    >>> from pyams_utils import json
    >>> from pyams_utils.timezone import UTC

    >>> stock_json.dumps('my string')
    '"my string"'

    >>> stock_json.dumps({'key': 'value'})
    '{"key": "value"}'

    >>> value = datetime.fromtimestamp(1205000000, UTC)
    >>> stock_json.dumps(value)
    '"2008-03-08T18:13:20+00:00"'
"""

import json

from datetime import date, datetime

__docformat__ = 'restructuredtext'


def default_json_encoder(obj):
    """Default JSON encoding of dates and datetimes"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj


# pylint: disable=protected-access
json._default_encoder = json.JSONEncoder(skipkeys=False,
                                         ensure_ascii=True,
                                         check_circular=True,
                                         allow_nan=True,
                                         indent=None,
                                         separators=None,
                                         default=default_json_encoder)
