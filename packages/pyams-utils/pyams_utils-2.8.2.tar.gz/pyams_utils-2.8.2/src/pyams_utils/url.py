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

"""PyAMS_utils.url module

This module provides several functions, adapters and TALES extensions which can be used to
generate object's URLs.

Three kinds of URLs can be used:
 - an absolute URL, which is the standard way to access an object via it's physical path
 - a canonical URL; this URL is the "preferred" one used to access an object, and is typically
   used by search engines to index contents
 - a relative URL; some contents can use this kind of URL to get access to an object from another
   context.
"""

from pyramid.encode import url_quote, urlencode
from pyramid.url import QUERY_SAFE, resource_url
from zope.interface import Interface

from pyams_utils.adapter import ContextRequestAdapter, ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.tales import ITALESExtension
from pyams_utils.interfaces.url import ICanonicalURL, IRelativeURL
from pyams_utils.request import get_display_context
from pyams_utils.unicode import translate_string


__docformat__ = 'restructuredtext'


def generate_url(title, min_word_length=2):
    """Generate an SEO-friendly content URL from it's title

    The original title is translated to remove accents, converted to lowercase, and words
    shorter than three characters (by default) are removed; terms are joined by hyphens.

    :param title: the input text
    :param min_word_length: minimum length of words to keep

    >>> from pyams_utils.url import generate_url
    >>> generate_url('This is my test')
    'this-is-my-test'

    Single letters are removed from generated URLs:

    >>> generate_url('This word has a single a')
    'this-word-has-single'

    But you can define the minimum length of word:

    >>> generate_url('This word has a single a', min_word_length=4)
    'this-word-single'

    If input text contains slashes, they are replaced with hyphens:

    >>> generate_url('This string contains/slash')
    'this-string-contains-slash'

    Punctation and special characters are completely removed:

    >>> generate_url('This is a string with a point. And why not?')
    'this-is-string-with-point-and-why-not'
    """
    return '-'.join(filter(lambda x: len(x) >= min_word_length,
                           translate_string(title.replace('/', '-'), escape_slashes=False,
                                            force_lower=True, spaces='-', remove_punctuation=True,
                                            keep_chars='-').split('-')))


#
# Absolute URLs management
#

def absolute_url(context, request, view_name=None, query=None):
    """Get resource absolute_url

    :param object context: the persistent object for which absolute URL is required
    :param request: the request on which URL is based
    :param str view_name: an optional view name to add to URL
    :param str/dict query: an optional URL arguments string or mapping

    This absolute URL function is based on default Pyramid's :py:func:`resource_url` function, but
    add checks to remove some double slashes, and add control on view name when it begins with a '#'
    character which is used by MyAMS.js framework.
    """

    # if we pass a string to absolute_url(), argument is returned as-is!
    if isinstance(context, str):
        return context

    # if we have several parents without name in the lineage, the resource URL contains a double
    # slash which generates "NotFound" exceptions; so we replace it with a single slash...
    result = resource_url(context, request).replace('//', '/').replace(':/', '://')
    if result.endswith('/'):
        result = result[:-1]
    if view_name:
        if view_name.startswith('#'):
            result += view_name
        else:
            result += '/' + view_name
    if query:
        qstr = ''
        if isinstance(query, str):
            qstr = '?' + url_quote(query, QUERY_SAFE)
        elif query:
            qstr = '?' + urlencode(query, doseq=True)
        result += qstr
    return result


@adapter_config(name='absolute_url',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class AbsoluteUrlTalesExtension(ContextRequestViewAdapter):
    """tales:absolute_url(context, view_name) TALES extension

    A PyAMS TALES extension used to get access to an object URL from a page template.
    """

    def render(self, context=None, view_name=None, **params):
        """Extension rendering; see
        :py:class:`ITALESExtension <pyams_utils.interfaces.tales.ITALESExtension>`
        """
        if context is None:
            context = self.context
        return absolute_url(context, self.request, view_name, params)


#
# Canonical URLs management
#

def canonical_url(context, request, view_name=None, query=None):
    """Get resource canonical URL

    We look for an :py:class:`ICanonicalURL <pyams_utils.interfaces.url.ICanonicalURL>` adapter;
    if none is found, we use the absolute_url.
    """

    # if we pass a string to canonical_url(), argument is returned as-is!
    if isinstance(context, str):
        return context

    url_adapter = request.registry.queryMultiAdapter((context, request), ICanonicalURL)
    if url_adapter is None:
        url_adapter = request.registry.queryAdapter(context, ICanonicalURL)

    if url_adapter is not None:
        return url_adapter.get_url(view_name, query)
    return absolute_url(context, request, view_name, query)


@adapter_config(name='canonical_url',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class CanonicalUrlTalesExtension(ContextRequestViewAdapter):
    """tales:canonical_url(context, view_name) TALES extension

    A PyAMS TALES extension used to get access to an object's canonical URL from a page template.
    """

    def render(self, context=None, view_name=None, **params):
        """Render TALES extension; see
        :py:class:`ITALESExtension <pyams_utils.interfaces.tales.ITALESExtension>`
        """
        if context is None:
            context = self.context
        return canonical_url(context, self.request, view_name, params)


#
# Relative URLs management
#

@adapter_config(required=(Interface, Interface), provides=IRelativeURL)
class DefaultRelativeURLAdapter(ContextRequestAdapter):
    """Default relative URL adapter"""

    def get_url(self, display_context=None, view_name=None, query=None):
        # pylint: disable=unused-argument
        """Default adapter returns absolute URL"""
        return absolute_url(self.context, self.request, view_name, query)


def relative_url(context, request, display_context=None, view_name=None, query=None):
    """Get resource URL relative to given context"""
    if display_context is None:
        display_context = get_display_context(request)
    adapter = request.registry.getMultiAdapter((context, request), IRelativeURL)
    return adapter.get_url(display_context, view_name, query)


@adapter_config(name='relative_url',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class RelativeUrlTalesExtension(ContextRequestViewAdapter):
    """tales:relative_url(context, view_name, query) TALES extension

    A PyAMS TALES extension used to get an object's relative URL based on current request display
    context.
    """

    def render(self, context=None, view_name=None, query=None):
        """Render TALES extension;
        see :py:class:`ITALESExtension <pyams_utils.interfaces.tales.ITALESExtension>`
        """
        if context is None:
            context = self.context
        return relative_url(context, self.request, view_name=view_name, query=query)
