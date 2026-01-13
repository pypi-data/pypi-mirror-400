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

"""PyAMS_utils.interfaces.url module

These interfaces are used to define different types of URLs which can be used in a web site.
These includes absolute URLs, canonical URLs and related URLs.

See :py:mod:`PyAMS URL module <pyams_utils.url>` for a longer description.
"""

from zope.interface import Interface


__docformat__ = 'restructuredtext'


class ICanonicalURL(Interface):
    """Interface used to get content's canonical URL"""

    def get_url(self, view_name=None, query=None):
        """Get content's canonical URL"""


class IRelativeURL(Interface):
    """Get content URL based on another context"""

    def get_url(self, display_context=None, view_name=None, query=None):
        """Get content URL relative to given display context"""
