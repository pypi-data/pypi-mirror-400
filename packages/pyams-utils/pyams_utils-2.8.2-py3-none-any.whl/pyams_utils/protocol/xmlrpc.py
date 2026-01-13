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

"""PyAMS_utils.protocol.xmlrpc module

This module provides a few set of classes and functions usable to improve XML-RPC client usage.

It provides custom transports and allows storage of response cookies
"""

import base64
import http.client
import http.cookiejar
import socket
import urllib.request
import xmlrpc.client

import pkg_resources
from pkg_resources import DistributionNotFound


try:
    import gzip
except ImportError:
    gzip = None  # python can be built without zlib/gzip support

__docformat__ = 'restructuredtext'


class XMLRPCCookieAuthTransport(xmlrpc.client.Transport):
    # pylint: disable=too-many-instance-attributes
    """An XML-RPC transport handling authentication via cookies"""

    _http_connection = http.client.HTTPConnection
    verbose = False

    def __init__(self, user_agent, credentials=(), cookies=None,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT, headers=None):
        # pylint: disable=protected-access,too-many-arguments
        xmlrpc.client.Transport.__init__(self)
        self.user_agent = user_agent
        self.credentials = credentials
        self.cookies = cookies
        self.timeout = timeout
        self.headers = headers

    def request(self, host, handler, request_body, verbose=False):
        self.verbose = verbose
        # issue XML-RPC request
        connection = self.send_request(host, handler, request_body, verbose)
        # get response
        return self.get_response(connection, host, handler)

    def make_connection(self, host):
        # This is the make_connection that runs under Python 2.7 and newer.
        # The code is pulled straight from 2.7 xmlrpclib, except replacing
        # HTTPConnection with self._http_connection
        if self._connection and host == self._connection[0]:
            return self._connection[1]
        chost, self._extra_headers, _x509 = self.get_host_info(host)
        self._connection = host, self._http_connection(chost, timeout=self.timeout)
        return self._connection[1]

    def send_request(self, host, handler, request_body, debug):
        connection = self.make_connection(host)
        headers = self._extra_headers[:]
        if debug:
            connection.set_debuglevel(1)
        if self.accept_gzip_encoding and gzip:
            connection.putrequest("POST", handler, skip_accept_encoding=True)
            headers.append(("Accept-Encoding", "gzip"))
        else:
            connection.putrequest("POST", handler)
        self.send_auth(connection)
        self.send_content_type(connection)
        self.send_user_agent(connection)
        self.send_headers(connection, headers)
        self.send_content(connection, request_body)
        return connection

    def send_auth(self, connection):
        """Override the send_host hook to also send authentication info"""
        if (self.cookies is not None) and (len(self.cookies) > 0):
            for cookie in self.cookies:
                connection.putheader('Cookie', '%s=%s' % (cookie.name, cookie.value))
        elif self.credentials:
            creds = base64.encodebytes(("%s:%s" % self.credentials).encode()).strip().decode()
            auth = 'Basic %s' % creds
            connection.putheader('Authorization', auth)

    @staticmethod
    def send_content_type(connection):
        """Send content type"""
        connection.putheader('Content-Type', 'text/xml')

    def send_user_agent(self, connection):
        """Send user agent"""
        connection.putheader('User-Agent', self.user_agent)

    def send_headers(self, connection, headers):
        """Send custom headers"""
        xmlrpc.client.Transport.send_headers(self, connection, headers)
        for key, value in (self.headers or {}).items():
            connection.putheader(key, value)

    class CookieRequest(urllib.request.Request):
        """Dummy request class used for extracting cookies"""

    class CookieResponseHelper:
        """Dummy response headers helper"""

        def __init__(self, response):
            self.response = response

        def getheaders(self, header):
            """Get response headers"""
            return self.response.msg.getallmatchingheaders(header)

    class CookieResponse:
        """Dummy response class used to extract cookies"""

        def __init__(self, response):
            self.response = response

        def info(self):
            """Get response info from cookies"""
            return XMLRPCCookieAuthTransport.CookieResponseHelper(self.response)

    def get_response(self, connection, host, handler):
        """Get server response"""
        response = connection.getresponse()
        # extract cookies from response headers
        if self.cookies is not None:
            crequest = XMLRPCCookieAuthTransport.CookieRequest('http://%s/' % host)
            cresponse = XMLRPCCookieAuthTransport.CookieResponse(response)
            for cookie in self.cookies.make_cookies(cresponse, crequest):
                if cookie.name.startswith('Set-Cookie'):
                    cookie.name = cookie.name.split(': ', 1)[1]
                self.cookies.set_cookie(cookie)
        if response.status != 200:
            raise xmlrpc.client.ProtocolError(host + handler, response.status, response.reason,
                                              response.getheaders())
        return self.parse_response(response)


class SecureXMLRPCCookieAuthTransport(XMLRPCCookieAuthTransport):
    """Secure XML-RPC transport"""

    _http_connection = http.client.HTTPSConnection


try:
    CLIENT_VERSION = pkg_resources.get_distribution('pyams_utils').version
except DistributionNotFound:
    CLIENT_VERSION = 'dev'


def get_client(uri, credentials=(), verbose=False, allow_none=0,
               timeout=socket._GLOBAL_DEFAULT_TIMEOUT, headers=None):
    # pylint: disable=protected-access,too-many-arguments
    """Get an XML-RPC client which supports basic authentication"""
    if uri.startswith('https:'):
        transport = SecureXMLRPCCookieAuthTransport(
            f'Python XML-RPC Client/{CLIENT_VERSION} (PyAMS secure transport)',
            credentials, timeout=timeout, headers=headers)
    else:
        transport = XMLRPCCookieAuthTransport(
            f'Python XML-RPC Client/{CLIENT_VERSION} (PyAMS basic transport)',
            credentials, timeout=timeout, headers=headers)
    return xmlrpc.client.Server(uri, transport=transport,
                                verbose=verbose, allow_none=allow_none)


def get_client_with_cookies(uri, credentials=(), verbose=False, allow_none=0,
                            timeout=socket._GLOBAL_DEFAULT_TIMEOUT, headers=None, cookies=None):
    # pylint: disable=protected-access,too-many-arguments
    """Get an XML-RPC client which supports authentication through cookies"""
    if cookies is None:
        cookies = http.cookiejar.CookieJar()
    if uri.startswith('https:'):
        transport = SecureXMLRPCCookieAuthTransport(
            f'Python XML-RPC Client/{CLIENT_VERSION} (PyAMS secure cookie transport)',
            credentials, cookies, timeout, headers)
    else:
        transport = XMLRPCCookieAuthTransport(
            f'Python XML-RPC Client/{CLIENT_VERSION} (PyAMS basic cookie transport)',
            credentials, cookies, timeout, headers)
    return xmlrpc.client.Server(uri, transport=transport,
                                verbose=verbose, allow_none=allow_none)
