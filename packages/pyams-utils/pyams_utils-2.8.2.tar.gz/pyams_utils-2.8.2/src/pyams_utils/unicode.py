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

"""PyAMS_utils.unicode module

This module provides a small set of functions which can be used to handle unicode data and
their bytes equivalent.
"""

import codecs
import string

__docformat__ = 'restructuredtext'


_UNICODE_TRANS_TABLE = {}


def _fill_unicode_trans_table():
    _corresp = [
        ("A", [0x00C0, 0x00C1, 0x00C2, 0x00C3, 0x00C4, 0x00C5, 0x0100, 0x0102, 0x0104]),
        ("AE", [0x00C6]),
        ("a", [0x00E0, 0x00E1, 0x00E2, 0x00E3, 0x00E4, 0x00E5, 0x0101, 0x0103, 0x0105]),
        ("ae", [0x00E6]),
        ("C", [0x00C7, 0x0106, 0x0108, 0x010A, 0x010C]),
        ("c", [0x00E7, 0x0107, 0x0109, 0x010B, 0x010D]),
        ("D", [0x00D0, 0x010E, 0x0110]),
        ("d", [0x00F0, 0x010F, 0x0111]),
        ("E", [0x00C8, 0x00C9, 0x00CA, 0x00CB, 0x0112, 0x0114, 0x0116, 0x0118, 0x011A]),
        ("e", [0x00E8, 0x00E9, 0x00EA, 0x00EB, 0x0113, 0x0115, 0x0117, 0x0119, 0x011B]),
        ("G", [0x011C, 0x011E, 0x0120, 0x0122]),
        ("g", [0x011D, 0x011F, 0x0121, 0x0123]),
        ("H", [0x0124, 0x0126]),
        ("h", [0x0125, 0x0127]),
        ("I", [0x00CC, 0x00CD, 0x00CE, 0x00CF, 0x0128, 0x012A, 0x012C, 0x012E, 0x0130]),
        ("i", [0x00EC, 0x00ED, 0x00EE, 0x00EF, 0x0129, 0x012B, 0x012D, 0x012F, 0x0131]),
        ("IJ", [0x0132]),
        ("ij", [0x0133]),
        ("J", [0x0134]),
        ("j", [0x0135]),
        ("K", [0x0136]),
        ("k", [0x0137, 0x0138]),
        ("L", [0x0139, 0x013B, 0x013D, 0x013F, 0x0141]),
        ("l", [0x013A, 0x013C, 0x013E, 0x0140, 0x0142]),
        ("N", [0x00D1, 0x0143, 0x0145, 0x0147, 0x014A]),
        ("n", [0x00F1, 0x0144, 0x0146, 0x0148, 0x0149, 0x014B]),
        ("O", [0x00D2, 0x00D3, 0x00D4, 0x00D5, 0x00D6, 0x00D8, 0x014C, 0x014E, 0x0150]),
        ("o", [0x00B0, 0x00F2, 0x00F3, 0x00F4, 0x00F5, 0x00F6, 0x00F8, 0x014D, 0x014F, 0x0151]),
        ("OE", [0x0152]),
        ("oe", [0x0153]),
        ("R", [0x0154, 0x0156, 0x0158]),
        ("r", [0x0155, 0x0157, 0x0159]),
        ("S", [0x015A, 0x015C, 0x015E, 0x0160]),
        ("s", [0x015B, 0x015D, 0x015F, 0x01610, 0x017F]),
        ("T", [0x0162, 0x0164, 0x0166]),
        ("t", [0x0163, 0x0165, 0x0167]),
        ("U", [0x00D9, 0x00DA, 0x00DB, 0x00DC, 0x0168, 0x016A, 0x016C, 0x016E, 0x0170, 0x172]),
        ("u", [0x00F9, 0x00FA, 0x00FB, 0x00FC, 0x0169, 0x016B, 0x016D, 0x016F, 0x0171]),
        ("W", [0x0174]),
        ("w", [0x0175]),
        ("Y", [0x00DD, 0x0176, 0x0178]),
        ("y", [0x00FD, 0x00FF, 0x0177]),
        ("Z", [0x0179, 0x017B, 0x017D]),
        ("z", [0x017A, 0x017C, 0x017E]),
        ("'", [0x2019])
    ]
    for char, codes in _corresp:
        for code in codes:
            _UNICODE_TRANS_TABLE[code] = char


_fill_unicode_trans_table()


_REMOVED_CHARS = '®©™…'
"""List of custom characters to remove from input strings"""


def translate_string(value, escape_slashes=False, force_lower=True,
                     spaces=' ', remove_punctuation=True, keep_chars='_-.'):
    # pylint: disable=too-many-arguments
    """Remove extended characters and diacritics from string and replace them with 'basic' ones

    :param str value: text to be translated
    :param boolean escape_slashes: if True, slashes are also converted
    :param boolean force_lower: if True, result is automatically converted to lower case
    :param str spaces: character used to replace spaces
    :param boolean remove_punctuation: if True, all punctuation characters are removed
    :param str keep_chars: characters which may be kept in the input string
    :return: text without diacritics or special characters

    >>> from pyams_utils.unicode import translate_string
    >>> input_string = 'Ceci est un test en Français !!!'
    >>> translate_string(input_string)
    'ceci est un test en francais'
    >>> translate_string(input_string, force_lower=False)
    'Ceci est un test en Francais'
    >>> translate_string(input_string, spaces='-')
    'ceci-est-un-test-en-francais'
    >>> translate_string(input_string, remove_punctuation=False)
    'ceci est un test en francais !!!'
    >>> translate_string(input_string, keep_chars='!')
    'ceci est un test en francais !!!'
    """
    if escape_slashes:
        value = value.replace("\\", "/").split("/")[-1]
    value = value.strip()
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    value = value.translate(_UNICODE_TRANS_TABLE)
    if remove_punctuation:
        punctuation = ''.join(filter(lambda x: x not in keep_chars,
                                     string.punctuation + _REMOVED_CHARS))
        value = ''.join(filter(lambda x: x not in punctuation, value))
    if force_lower:
        value = value.lower()
    value = value.strip()
    if spaces != ' ':
        value = value.replace(' ', spaces)
    return value


def nvl(value, default=''):
    """Get specified value, or an empty string if value is empty

    :param object value: value to be checked
    :param object default: default value to be returned if value is *false*
    :return: input value, or *default* if value is *false*

    >>> from pyams_utils.unicode import nvl
    >>> nvl(None)
    ''
    >>> nvl('foo')
    'foo'
    >>> nvl(False, 'bar')
    'bar'
    """
    return value or default


def uninvl(value, default='', encoding='utf-8'):
    """Get specified value converted to unicode, or an empty unicode string if value is empty

    :param str/bytes value: the input to be checked
    :param default: str; default value
    :param encoding: str; encoding name to use for conversion
    :return: str; value, or *default* if value is empty, converted to unicode

    >>> from pyams_utils.unicode import uninvl
    >>> uninvl('String value')
    'String value'
    >>> uninvl(b'String value')
    'String value'
    >>> uninvl(b'Cha\\xc3\\xaene accentu\\xc3\\xa9e')
    'Chaîne accentuée'
    >>> uninvl(b'Cha\\xeene accentu\\xe9e', 'latin1')
    'Chaîne accentuée'
    """
    if isinstance(value, str):
        return value
    try:
        return codecs.decode(value or default, encoding)
    except ValueError:
        return codecs.decode(value or default, 'latin1')


def unidict(value, encoding='utf-8'):
    """Get specified dict with values converted to unicode

    :param dict value: input mapping of strings which may be converted to unicode
    :param str encoding: output encoding
    :return: dict; a new mapping with each value converted to unicode

    >>> from pyams_utils.unicode import unidict
    >>> unidict({'input': b'Cha\\xc3\\xaene accentu\\xc3\\xa9e'})
    {'input': 'Chaîne accentuée'}
    >>> unidict({'input': b'Cha\\xeene accentu\\xe9e'}, 'latin1')
    {'input': 'Chaîne accentuée'}
    """
    result = {}
    for key in value:
        result[key] = uninvl(value[key], encoding)
    return result


def unilist(value, encoding='utf-8'):
    """Get specified list with values converted to unicode

    :param list value: input list of strings which may be converted to unicode
    :param str encoding: output encoding
    :return: list; a new list with each value converted to unicode

    >>> from pyams_utils.unicode import unilist
    >>> unilist([b'Cha\\xc3\\xaene accentu\\xc3\\xa9e'])
    ['Chaîne accentuée']
    >>> unilist([b'Cha\\xeene accentu\\xe9e'], 'latin1')
    ['Chaîne accentuée']
    """
    if not isinstance(value, (list, tuple)):
        return uninvl(value, encoding)
    return [uninvl(v, encoding) for v in value]


def encode(value, encoding='utf-8'):
    """Encode given Unicode value to bytes with given encoding

    :param str value: the value to encode
    :param str encoding: selected encoding
    :return: bytes; value encoded to bytes if input is a string, original value otherwise

    >>> from pyams_utils.unicode import encode
    >>> encode('Chaîne accentuée')
    b'Cha\\xc3\\xaene accentu\\xc3\\xa9e'
    >>> encode('Chaîne accentuée', 'latin1')
    b'Cha\\xeene accentu\\xe9e'
    """
    return value.encode(encoding) if isinstance(value, str) else value


def utf8(value):
    """Encode given unicode value to UTF-8 encoded bytes

    :param str value: the value to encode to utf-8
    :return: bytes; value encoded to bytes if input is a string, original value otherwise

    >>> from pyams_utils.unicode import utf8
    >>> utf8('Chaîne accentuée')
    b'Cha\\xc3\\xaene accentu\\xc3\\xa9e'
    """
    return encode(value, 'utf-8')


def decode(value, encoding='utf-8'):
    """Decode given bytes value to unicode with given encoding

    :param bytes value: the value to decode
    :param str encoding: selected encoding
    :return: str; value decoded to unicode string if input is a bytes, original value otherwise

    >>> from pyams_utils.unicode import decode
    >>> decode(b'Cha\\xc3\\xaene accentu\\xc3\\xa9e')
    'Chaîne accentuée'
    >>> decode(b'Cha\\xeene accentu\\xe9e', 'latin1')
    'Chaîne accentuée'
    """
    return value.decode(encoding) if isinstance(value, bytes) else value
