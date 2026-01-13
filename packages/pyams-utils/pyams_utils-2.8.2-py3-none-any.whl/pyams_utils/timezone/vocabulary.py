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

"""PyAMS_utils.timezone.vocabulary module

This module provides a vocabulary of available timezones
"""

import pytz
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_utils.interfaces import TIMEZONES_VOCABULARY_NAME
from pyams_utils.vocabulary import vocabulary_config


__docformat__ = 'restructuredtext'


@vocabulary_config(name=TIMEZONES_VOCABULARY_NAME)
class TimezonesVocabulary(SimpleVocabulary):
    """Timezones vocabulary"""

    def __init__(self, *args, **kw):  # pylint: disable=unused-argument
        terms = [SimpleTerm(t, t, t) for t in pytz.all_timezones]
        super().__init__(terms)
