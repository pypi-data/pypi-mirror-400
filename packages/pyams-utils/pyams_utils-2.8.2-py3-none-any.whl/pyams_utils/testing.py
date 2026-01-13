#
# Copyright (c) 2007 Zope Foundation and Contributors.
# Copyright (c) 2015-2020 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.testing module

This module provides small testing helpers.
"""

import sys

import lxml.etree
import lxml.html

from fanstatic import Library, Resource
from fanstatic.core import set_resource_file_existence_checking


__docformat__ = 'restructuredtext'


class DummyVenusianInfo:
    """Dummy venusian info"""

    scope = 'notaclass'
    module = sys.modules['pyams_utils.testing']
    codeinfo = 'codeinfo'


class DummyVenusian:
    """Dummy venusian class"""

    def __init__(self, info=None):
        if info is None:
            info = DummyVenusianInfo()
        self.info = info
        self.attachments = []

    def attach(self, wrapped, callback, category=None, depth=1):
        """Venusian attachment"""
        self.attachments.append((wrapped, callback, category, depth))
        return self.info


class DummyVenusianContext:
    """Dummy venusian context"""

    def __init__(self, config):
        self.config = config


def call_venusian(venusian, config, context=None):
    """Call venusian decorator"""
    if context is None:
        context = DummyVenusianContext(config)
    # pylint: disable=unused-variable
    for wrapped, callback, category, depth in venusian.attachments:
        callback(context, None, wrapped)
    return context.config


def call_decorator(config, decorator, handler, *args, **kwargs):
    """Call a venusian decorator for testing"""
    venusian = DummyVenusian()
    target = decorator(registry=config.registry, *args, **kwargs)
    target.venusian = venusian
    target(handler)
    call_venusian(venusian, config)


def render_xpath(view, xpath='.'):
    """Render only an XPath selection of a full HTML code

    >>> from pyams_utils.testing import render_xpath
    >>> class View:
    ...     def __call__(self):
    ...         return '''<div><div class="row"><p>Row 1</p></div> \
                          <div class="row"><p>Row 2</p></div></div>'''
    >>> view = View()
    >>> render_xpath(view, './/div[2][@class="row"]')
    '<div class="row">\\n  <p>Row 2</p>\\n</div>\\n'
    >>> render_xpath(view, './/div[2][@class="bad"]')
    Traceback (most recent call last):
    ...
    ValueError: No elements matched by './/div[2][@class="bad"]'.
    """
    method = getattr(view, 'render', None)
    if method is None:
        method = view.__call__

    string = method()
    if string == "":
        return string

    try:
        root = lxml.etree.fromstring(string)  # pylint: disable=c-extension-no-member
    except lxml.etree.XMLSyntaxError:  # pylint: disable=c-extension-no-member
        root = lxml.html.fromstring(string)

    result = ""
    for node in root.xpath(xpath, namespaces={'xmlns': 'http://www.w3.org/1999/xhtml'}):
        # pylint: disable=c-extension-no-member
        out = lxml.etree.tounicode(node, pretty_print=True)
        out = out.replace(' xmlns="http://www.w3.org/1999/xhtml"', ' ')
        result += out

    if not result:
        raise ValueError("No elements matched by %s." % repr(xpath))

    # let's get rid of blank lines
    result = result.replace('\n\n', '\n')

    # self-closing tags are more readable with a space before the
    # end-of-tag marker
    result = result.replace('"/>', '" />')

    return result


def format_html(input):  # pylint: disable=redefined-builtin
    """Render formatted HTML code by removing empty lines and spaces ending lines

    >>> from pyams_utils.testing import format_html
    >>> format_html('''<div>      \\n<b>This is a test</b>    \\n\\n</div>    ''')
    '<div>\\n<b>This is a test</b>\\n</div>'
    """
    return '\n'.join(filter(bool, map(str.rstrip, input.split('\n'))))


if sys.argv[-1].endswith('/bin/test'):

    library = Library('foo', '')  # pylint: disable=invalid-name

    set_resource_file_existence_checking(False)
    res_x1 = Resource(library, 'x1.js')  # pylint: disable=invalid-name
    res_x1.dependency_nr = 0
    set_resource_file_existence_checking(True)
