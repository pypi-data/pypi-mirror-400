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

"""PyAMS_utils.i18n module

This module is used to get browser language from request
"""

import locale


__docformat__ = 'restructuredtext'


def normalize_lang(lang):
    """Normalize input languages string

    >>> from pyams_utils.i18n import normalize_lang
    >>> lang = 'fr,en_US ; q=0.9, en-GB ; q=0.8, en ; q=0.7'
    >>> normalize_lang(lang)
    'fr,en-us;q=0.9,en-gb;q=0.8,en;q=0.7'
    """
    return lang.strip() \
               .lower() \
               .replace('_', '-') \
               .replace(' ', '')


def get_browser_language(request):
    """Custom locale negotiator

    Copied from zope.publisher code

    >>> from pyramid.testing import DummyRequest
    >>> from pyams_utils.i18n import get_browser_language

    >>> request = DummyRequest()
    >>> request.headers['Accept-Language'] = 'fr, en_US ; q=0.9, en-GB ; q=bad, es; ' + \
                                             'q=0.8, en ; q=0.7'
    >>> get_browser_language(request)
    'fr'
    """
    accept_langs = request.headers.get('Accept-Language', '').split(',')

    # Normalize lang strings
    accept_langs = [normalize_lang(l) for l in accept_langs]
    # Then filter out empty ones
    accept_langs = [l for l in accept_langs if l]

    accepts = []
    for index, lang in enumerate(accept_langs):
        lang_item = lang.split(';', 2)

        # If not supplied, quality defaults to 1...
        quality = 1.0

        if len(lang_item) == 2:
            qual = lang_item[1]
            if qual.startswith('q='):
                qual = qual.split('=', 2)[1]
                try:
                    quality = float(qual)
                except ValueError:
                    # malformed quality value, skip it.
                    continue

        if quality == 1.0:
            # ... but we use 1.9 - 0.001 * position to
            # keep the ordering between all items with
            # 1.0 quality, which may include items with no quality
            # defined, and items with quality defined as 1.
            quality = 1.9 - (0.001 * index)

        accepts.append((quality, lang_item[0]))

    # Filter langs with q=0, which means
    # unwanted lang according to the spec
    # See: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
    accepts = [acc for acc in accepts if acc[0]]

    accepts.sort()
    accepts.reverse()

    return [lang for _, lang in accepts][0] if accepts else None


def set_locales(settings):
    """Define locale environment variables

    :param settings: Pyramid's settings object
    """
    for attr in ('LC_CTYPE', 'LC_COLLATE', 'LC_TIME', 'LC_MONETARY', 'LC_NUMERIC', 'LC_ALL'):
        value = settings.get(f'pyams.locale.{attr.lower()}')
        if value:
            locale.setlocale(getattr(locale, attr), value)
