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

"""PyAMS_utils.interfaces.tales module

TALES extensions are custom adapters which can be used to extend Chameleon and Zope templates.
"""

from zope.interface import Interface


__docformat__ = 'restructuredtext'


class ITALESExtension(Interface):
    """Custom TALES extension

    These extensions will be registered through adapters for
    (context, request, view) or (context, request).
    """

    def render(self, context=None):
        """Render extension

        This method can return HTML code which will be inserted directly into an HTML template,
        but can also return any value which will be assigned to a local template variable.
        """
