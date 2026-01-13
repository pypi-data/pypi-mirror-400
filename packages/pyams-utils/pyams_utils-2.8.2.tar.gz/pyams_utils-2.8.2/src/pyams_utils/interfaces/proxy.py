#
# Copyright (c) 2015-2023 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.interfaces.proxy module

This module defines an HTTP proxy configuration interface.
"""

from zope.interface import Interface
from zope.schema import Choice, Int, TextLine
from pyams_utils.schema import EncodedPasswordField


__docformat__ = 'restructuredtext'

from pyams_utils import _


class IProxyInfo(Interface):
    """Proxy information interface"""

    protocol = Choice(title=_("HTTP protocol"),
                      description=_("Protocol used to access HTTP proxy"),
                      required=False,
                      values=('http', 'https'),
                      default='http')

    host = TextLine(title=_("Proxy hostname"),
                    description=_("Host name of the proxy server"),
                    required=False)

    port = Int(title=_("Proxy port"),
               description=_("Port number used by the proxy server"),
               required=False,
               default=8080)

    username = TextLine(title=_("Proxy username"),
                        description=_("If the proxy server is requiring authentication, set the user name"),
                        required=False)

    password = EncodedPasswordField(title=_("Proxy password"),
                                    description=_("If the proxy server is requiring authentication, set "
                                                  "the user password"),
                                    required=False)

    selected_origins = TextLine(title=_("Selected origins"),
                                description=_("If proxy usage is restricted to several domains "
                                              "names, you can set them here, separated by comas"),
                                required=False)

    def get_proxy_url(self, request):
        """Return proxy configuration"""
