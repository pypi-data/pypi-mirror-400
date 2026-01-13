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

"""PyAMS_utils.interfaces.text module

This module defines interfaces provided by adapters which can be used to handle
objects to their HTML representation.

The ITextFragmentRenderer is an adapter interface which can be used to include dynamic
parts into a static string, which can be an SQL query or a JSON object used, for example,
as a request body or an Elasticsearch query.
"""

from zope.interface import Attribute, Interface


__docformat__ = 'restructuredtext'

from pyams_utils import _


class IHTMLRenderer(Interface):
    """HTML renderer interface

    HTML renderers are implemented as adapters for a source object (which can
    be a string) and a request, so that you can easily implement custom renderers
    for any object and/or for any request layer.
    """

    label = Attribute(_("Optional renderer label"))

    def render(self, **kwargs):
        """Render adapted text"""


class ITextRenderer(Interface):
    """Text renderer interface

    Text renderers are implemented as adapters which can be used to include dynamic values
    into a "static" string. This value can be as simple as the current datetime, or based on
    any contextual result returned, for example, by a web service.

    This kind of component can be used, for example, to include a dynamic value into a SQL
    or Elasticsearch query. The source text is transformed using the *render_text* function,
    which is looking for strings using the *{{renderer}}* syntax, where *renderer* should be
    the name of a registered text renderer adapter. Some renderers can accept arguments, which
    are then provided using *{{renderer:param1,param2}}* syntax.
    """

    def render(self, **kwargs):
        """Renderer adapter as text"""
