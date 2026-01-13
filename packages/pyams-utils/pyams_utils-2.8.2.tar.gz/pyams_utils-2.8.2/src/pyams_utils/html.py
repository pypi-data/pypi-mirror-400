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

"""PyAMS_utils.html module

This module provides functions which are used to convert HTML code to plain text, by extracting
useful text and removing all HTML tags.
"""

from html.parser import HTMLParser
from warnings import warn


__docformat__ = 'restructuredtext'


class MyHTMLParser(HTMLParser):
    """HTML parser"""
    data = ''
    entitydefs = {'amp': '&', 'lt': '<', 'gt': '>',
                  'nbsp': ' ',
                  'apos': "'", 'quot': '"',
                  'Agrave': 'À', 'Aacute': 'A', 'Acirc': 'Â', 'Atilde': 'A',
                  'Auml': 'Ä', 'Aring': 'A',
                  'AElig': 'AE',
                  'Ccedil': 'Ç',
                  'Egrave': 'É', 'Eacute': 'È', 'Ecirc': 'Ê', 'Euml': 'Ë',
                  'Igrave': 'I', 'Iacute': 'I', 'Icirc': 'I', 'Iuml': 'I',
                  'Ntilde': 'N',
                  'Ograve': 'O', 'Oacute': 'O', 'Ocirc': 'Ô', 'Otilde': 'O',
                  'Ouml': 'Ö', 'Oslash': '0',
                  'Ugrave': 'Ù', 'Uacute': 'U', 'Ucirc': 'Û', 'Uuml': 'Ü',
                  'Yacute': 'Y',
                  'THORN': 'T',
                  'agrave': 'à', 'aacute': 'a', 'acirc': 'â', 'atilde': 'a',
                  'auml': 'ä', 'aring': 'a', 'aelig': 'ae',
                  'ccedil': 'ç',
                  'egrave': 'è', 'eacute': 'é', 'ecirc': 'ê', 'euml': 'ë',
                  'igrave': 'i', 'iacute': 'i', 'icirc': 'î', 'iuml': 'ï',
                  'ntilde': 'n',
                  'ograve': 'o', 'oacute': 'o', 'ocirc': 'ô', 'otilde': 'o',
                  'ouml': 'ö', 'oslash': 'o',
                  'ugrave': 'ù', 'uacute': 'u', 'ucirc': 'û', 'uuml': 'ü',
                  'yacute': 'y',
                  'thorn': 't',
                  'yuml': 'ÿ'}

    charrefs = {34: '"', 38: '&', 39: "'",
                60: '<', 62: '>',
                192: 'À', 193: 'A', 194: 'Â', 195: 'A', 196: 'Ä', 197: 'A',
                198: 'AE',
                199: 'Ç',
                200: 'È', 201: 'É', 202: 'Ê', 203: 'Ë',
                204: 'I', 205: 'I', 206: 'Î', 207: 'Ï',
                208: 'D',
                209: 'N',
                210: 'O', 211: 'O', 212: 'Ô', 213: 'O', 214: 'Ö', 216: 'O',
                215: 'x',
                217: 'Ù', 218: 'U', 219: 'Û', 220: 'Ü',
                221: 'Y', 222: 'T',
                223: 'sz',
                224: 'à', 225: 'a', 226: 'â', 227: 'a', 228: 'ä', 229: 'a',
                230: 'ae',
                231: 'ç',
                232: 'è', 233: 'é', 234: 'ê', 235: 'ë',
                236: 'i', 237: 'i', 238: 'î', 239: 'ï',
                240: 'e',
                241: 'n',
                242: 'o', 243: 'o', 244: 'ô', 245: 'o', 246: 'ö', 248: 'o',
                249: 'ù', 250: 'u', 251: 'û', 252: 'ü',
                253: 'y', 255: 'ÿ'}

    def handle_data(self, data):
        if not data:
            return
        try:
            self.data += data
        except TypeError:
            self.data += data.decode('utf-8')

    def handle_entityref(self, name):
        self.data += self.entitydefs.get(name, '')

    def handle_charref(self, name):
        try:
            int_value = int(name)
        except ValueError:
            return
        if not 0 <= int_value <= 255:
            return
        self.handle_data(self.charrefs.get(int_value))

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            self.data += ' '
        elif tag == 'br':
            self.data += '\n'

    def handle_endtag(self, tag):
        if tag == 'p':
            self.data += '\n'

    def error(self, message):
        warn(message)


def html_to_text(value):
    """Utility function to extract text content from HTML

    >>> from pyams_utils.html import html_to_text

    >>> html_to_text(None)
    ''

    >>> html = '''<p>This is a HTML text part.</p>'''
    >>> html_to_text(html)
    'This is a HTML text part.\\n'

    >>> html = '''<p>This is text with french accents: <strong>é à è ù</strong></p>'''
    >>> html_to_text(html)
    'This is text with french accents: é à è ù\\n'

    HTML parser should handle entities correctly:

    >>> html = '''<div><p>Header</p><p>This is an &lt; &#242; &gt; entity.<br /></p></div>'''
    >>> print(html_to_text(html))
    Header
    This is an < o > entity.

    >>> html = '''<div><p>Header</p><p>This is an &lt;&nbsp;&eacute;&nbsp;&gt; ''' + \
               '''entity.<br /></p></div>'''
    >>> print(html_to_text(html))
    Header
    This is an < é > entity.

    >>> html = '''<div><p>Head</p><p><table><tr><td>This is my test</td></tr></table></p></div>'''
    >>> print(html_to_text(html))
    Head
    This is my test

You can also insert invalid characters:

    >>> html = '''<div><p>Invalid &toto; &#712; &#str; characters</p></div>'''
    >>> print(html_to_text(html))
    Invalid   &#str; characters

    """
    if value is None:
        return ''
    parser = MyHTMLParser(convert_charrefs=False)
    parser.feed(value)
    parser.close()
    return parser.data
