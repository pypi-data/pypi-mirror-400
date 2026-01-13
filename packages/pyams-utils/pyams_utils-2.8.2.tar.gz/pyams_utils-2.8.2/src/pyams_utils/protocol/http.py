#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.protocol.http module

This module provides an HTTP client class, which allows to easilly define proxies and
authentication headers.
"""

import urllib.parse
import httplib2

from persistent import Persistent
from zope.schema.fieldproperty import FieldProperty

from pyams_utils.factory import factory_config
from pyams_utils.interfaces.proxy import IProxyInfo


__docformat__ = 'restructuredtext'


@factory_config(IProxyInfo)
class ProxyInfo(Persistent):
    """Proxy persistent information"""

    protocol = FieldProperty(IProxyInfo['protocol'])
    host = FieldProperty(IProxyInfo['host'])
    port = FieldProperty(IProxyInfo['port'])
    username = FieldProperty(IProxyInfo['username'])
    password = FieldProperty(IProxyInfo['password'])
    selected_origins = FieldProperty(IProxyInfo['selected_origins'])

    def __bool__(self):
        return bool(self.host and self.port)

    def get_proxy_url(self, request):
        """Proxy URL getter"""
        if not self.host:
            return None
        if self.selected_origins:
            domains = map(str.strip, self.selected_origins.split(','))
            if request.host not in domains:
                return None
        return '{}://{}{}:{}/'.format(self.protocol,
                                      '{}{}{}@'.format(self.username or '',
                                                       ':' if self.password else '',
                                                       self.password or '')
                                      if self.username else '',
                                      self.host,
                                      self.port)


class HTTPClient:
    # pylint: disable=too-many-instance-attributes
    """HTTP client with proxy support"""

    def __init__(self, method, protocol, servername, url, params=None, credentials=(),
                 proxy=(), rdns=True, proxy_auth=(), timeout=None, headers=None):
        # pylint: disable=too-many-arguments
        """Initialize HTTP connection"""
        self.connection = None
        self.method = method
        self.protocol = protocol
        self.servername = servername
        self.url = url
        self.params = params or {}
        self.location = None
        self.credentials = credentials
        self.proxy = proxy
        self.rdns = rdns
        self.proxy_auth = proxy_auth
        self.timeout = timeout
        self.headers = headers or {}
        if 'User-Agent' not in self.headers:
            self.headers['User-Agent'] = 'PyAMS HTTP Client/1.0'

    def get_response(self):
        """Common HTTP request"""
        if self.proxy and (len(self.proxy) == 2):
            proxy_info = httplib2.ProxyInfo(
                httplib2.socks.PROXY_TYPE_HTTP,
                proxy_host=self.proxy[0],
                proxy_port=self.proxy[1],
                proxy_rdns=self.rdns,
                proxy_user=self.proxy_auth and self.proxy_auth[0] or None,
                proxy_pass=self.proxy_auth and self.proxy_auth[1] or None)
        else:
            proxy_info = None
        http = httplib2.Http(timeout=self.timeout, proxy_info=proxy_info)
        if self.credentials:
            http.add_credentials(self.credentials[0], self.credentials[1])
        uri = '%s://%s%s' % (self.protocol, self.servername, self.url)
        if self.params:
            uri += '?' + urllib.parse.urlencode(self.params)
        response, content = http.request(uri, self.method, headers=self.headers)
        return response, content


def get_client(method, protocol, servername, url, params=None, credentials=(), proxy=(),
               rdns=True, proxy_auth=(), timeout=None, headers=None):
    # pylint: disable=too-many-arguments
    """HTTP client factory"""
    return HTTPClient(method, protocol, servername, url, params, credentials, proxy,
                      rdns, proxy_auth, timeout, headers)


def get_client_from_url(url, credentials=(), proxy=(), rdns=True, proxy_auth=(), timeout=None,
                        headers=None):
    # pylint: disable=too-many-arguments
    """HTTP client factory from URL"""
    elements = urllib.parse.urlparse(url)
    return HTTPClient('GET', elements.scheme, elements.netloc, elements.path, elements.params,
                      credentials, proxy, rdns, proxy_auth, timeout, headers)
