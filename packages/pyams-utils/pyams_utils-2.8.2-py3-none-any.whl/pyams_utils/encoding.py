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

"""PyAMS_utils.encoding module

This module defines a vocabulary of available encodings, as well as an "encoding" choice field.
"""

from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_utils.interfaces import ENCODINGS_VOCABULARY_NAME
from pyams_utils.request import check_request
from pyams_utils.vocabulary import vocabulary_config


__docformat__ = 'restructuredtext'

from pyams_utils import _


ENCODINGS = {
    'ascii': _('English (ASCII)'),
    'big5': _('Traditional Chinese (big5)'),
    'big5hkscs': _('Traditional Chinese (big5hkscs)'),
    'cp037': _('English (cp037)'),
    'cp424': _('Hebrew (cp424)'),
    'cp437': _('English (cp437)'),
    'cp500': _('Western Europe (cp500)'),
    'cp720': _('Arabic (cp720)'),
    'cp737': _('Greek (cp737)'),
    'cp775': _('Baltic languages (cp775)'),
    'cp850': _('Western Europe (cp850)'),
    'cp852': _('Central and Eastern Europe (cp852)'),
    'cp855': _('Bulgarian, Byelorussian, Macedonian, Russian, Serbian (cp855)'),
    'cp856': _('Hebrew (cp856)'),
    'cp857': _('Turkish (cp857)'),
    'cp858': _('Western Europe (cp858)'),
    'cp860': _('Portuguese (cp860)'),
    'cp861': _('Icelandic (cp861)'),
    'cp862': _('Hebrew (cp862)'),
    'cp863': _('Canadian (cp863)'),
    'cp864': _('Arabic (cp864)'),
    'cp865': _('Danish, Norwegian (cp865)'),
    'cp866': _('Russian (cp866)'),
    'cp869': _('Greek (cp869)'),
    'cp874': _('Thai (cp874)'),
    'cp875': _('Greek (cp875)'),
    'cp932': _('Japanese (cp932)'),
    'cp949': _('Korean (cp949)'),
    'cp950': _('Traditional Chinese (cp950)'),
    'cp1006': _('Urdu (cp1006)'),
    'cp1026': _('Turkish (cp1026)'),
    'cp1140': _('Western Europe (cp1140)'),
    'cp1250': _('Central and Eastern Europe (cp1250)'),
    'cp1251': _('Bulgarian, Byelorussian, Macedonian, Russian, Serbian (cp1251)'),
    'cp1252': _('Western Europe (cp1252)'),
    'cp1253': _('Greek (cp1253)'),
    'cp1254': _('Turkish (cp1254)'),
    'cp1255': _('Hebrew (cp1255)'),
    'cp1256': _('Arabic (cp1256)'),
    'cp1257': _('Baltic languages (cp1257)'),
    'cp1258': _('Vietnamese (cp1258)'),
    'euc-jp': _('Japanese (euc_jp)'),
    'euc-jis-2004': _('Japanese (euc_jis_2004)'),
    'euc-jisx0213': _('Japanese (euc_jisx0213)'),
    'euc-kr': _('Korean (euc_kr)'),
    'gb2312': _('Simplified Chinese (gb2312)'),
    'gbk': _('Unified Chinese (gbk)'),
    'gb18030': _('Unified Chinese (gb18030)'),
    'hz': _('Simplified Chinese (hz)'),
    'iso2022-jp': _('Japanese (iso2022_jp)'),
    'iso2022-jp-1': _('Japanese (iso2022_jp_1)'),
    'iso2022-jp-2': _('Japanese, Korean, Simplified Chinese, Western Europe, Greek (iso2022_jp_2)'),
    'iso2022-jp-2004': _('Japanese (iso2022_jp_2004)'),
    'iso2022-jp-3': _('Japanese (iso2022_jp_3)'),
    'iso2022-jp-ext': _('Japanese (iso2022_jp_ext)'),
    'iso2022-kr': _('Korean (iso2022_kr)'),
    'latin-1': _('West Europe (latin_1)'),
    'iso8859-2': _('Central and Eastern Europe (iso8859_2)'),
    'iso8859-3': _('Esperanto, Maltese (iso8859_3)'),
    'iso8859-4': _('Baltic languages (iso8859_4)'),
    'iso8859-5': _('Bulgarian, Byelorussian, Macedonian, Russian, Serbian (iso8859_5)'),
    'iso8859-6': _('Arabic (iso8859_6)'),
    'iso8859-7': _('Greek (iso8859_7)'),
    'iso8859-8': _('Hebrew (iso8859_8)'),
    'iso8859-9': _('Turkish (iso8859_9)'),
    'iso8859-10': _('Nordic languages (iso8859_10)'),
    'iso8859-13': _('Baltic languages (iso8859_13)'),
    'iso8859-14': _('Celtic languages (iso8859_14)'),
    'iso8859-15': _('Western Europe (iso8859_15)'),
    'iso8859-16': _('South-Eastern Europe (iso8859_16)'),
    'johab': _('Korean (johab)'),
    'koi8-r': _('Russian (koi8_r)'),
    'koi8-u': _('Ukrainian (koi8_u)'),
    'mac-cyrillic': _('Bulgarian, Byelorussian, Macedonian, Russian, Serbian (mac_cyrillic)'),
    'mac-greek': _('Greek (mac_greek)'),
    'mac-iceland': _('Icelandic (mac_iceland)'),
    'mac-latin2': _('Central and Eastern Europe (mac_latin2)'),
    'mac-roman': _('Western Europe (mac_roman)'),
    'mac-turkish': _('Turkish (mac_turkish)'),
    'ptcp154': _('Kazakh (ptcp154)'),
    'shift-jis': _('Japanese (shift_jis)'),
    'shift-jis-2004': _('Japanese (shift_jis_2004)'),
    'shift-jisx0213': _('Japanese (shift_jisx0213)'),
    'utf-32': _('all languages (utf_32)'),
    'utf-32-be': _('all languages (utf_32_be)'),
    'utf-32-le': _('all languages (utf_32_le)'),
    'utf-16': _('all languages (utf_16)'),
    'utf-16-be': _('all languages (BMP only - utf_16_be)'),
    'utf-16-le': _('all languages (BMP only - utf_16_le)'),
    'utf-7': _('all languages (utf_7)'),
    'utf-8': _('all languages (utf_8)'),
    'utf-8-sig': _('all languages (utf_8_sig)'),
}


@vocabulary_config(name=ENCODINGS_VOCABULARY_NAME)
class EncodingsVocabulary(SimpleVocabulary):
    """A vocabulary containing a set of registered encodings

    >>> from pyams_utils.encoding import ENCODINGS, EncodingsVocabulary
    >>> vocabulary = EncodingsVocabulary(None)
    >>> len(vocabulary._terms) == len(ENCODINGS)
    True
    """

    def __init__(self, context, *interfaces):  # pylint: disable=unused-argument
        request = check_request()
        translate = request.localizer.translate
        terms = [SimpleTerm(v, title=translate(t)) for v, t in ENCODINGS.items()]
        terms.sort(key=lambda x: x.title)
        super().__init__(terms, *interfaces)
