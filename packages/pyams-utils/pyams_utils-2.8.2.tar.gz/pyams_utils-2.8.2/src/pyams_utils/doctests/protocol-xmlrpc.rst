
===================================
PyAMS_utils xmlrpc protocol helpers
===================================

PyAMS_utils provides an "xmlrpc" module which helps using XML-RPC protocol:

    >>> from pyramid.testing import DummyRequest
    >>> from unittest.mock import patch
    >>> from http.client import HTTPConnection


Testing raw XML-RPC transport
-----------------------------

PyAMS_utils provides a custom XML-RPC transport to handle authentification and cookies:

    >>> from pyams_utils.protocol.xmlrpc import XMLRPCCookieAuthTransport

    >>> transport = XMLRPCCookieAuthTransport('PyAMS_utils XML-RPC client')
    >>> with patch.object(transport, '_http_connection') as connection:
    ...     request = transport.send_request('localhost', '/api/xmlrpc', '', True)

We can also get cookies:

    >>> from http.cookiejar import CookieJar, Cookie
    >>> cookies = CookieJar()
    >>> transport = XMLRPCCookieAuthTransport('PyAMS_utils XML-RPC client',
    ...                                       credentials=('admin', 'admin'),
    ...                                       cookies=cookies)
    >>> with patch.object(transport, '_http_connection') as connection:
    ...     request = transport.send_request('localhost', '/api/xmlrpc', '', True)
    ...     with patch.object(transport, 'send_request') as send_request:
    ...         response = send_request.get_response(connection, 'localhost', '/api/xmlrpc')


Using XML-RPC client
--------------------

PyAMS_utils provides a simple XML-RPC client factory:

    >>> from pyams_utils.protocol.xmlrpc import get_client

    >>> service = get_client('http://localhost/api/xmlrpc')
    >>> service
    <ServerProxy for localhost/api/xmlrpc>
    >>> with patch.object(XMLRPCCookieAuthTransport, 'request') as proxy:
    ...     response = service.get()

    >>> service = get_client('https://localhost/api/xmlrpc')
    >>> service
    <ServerProxy for localhost/api/xmlrpc>
    >>> with patch.object(XMLRPCCookieAuthTransport, 'request') as proxy:
    ...     response = service.get()


Using XML-RPC with cookies
--------------------------

If required, you can use an XML-RPC implementation supporting cookies to store server
information:

    >>> from pyams_utils.protocol.xmlrpc import get_client_with_cookies

    >>> service = get_client_with_cookies('http://localhost/api/xmlrpc')
    >>> service
    <ServerProxy for localhost/api/xmlrpc>
    >>> with patch.object(XMLRPCCookieAuthTransport, 'request') as proxy:
    ...     response = service.get()

    >>> service = get_client_with_cookies('https://localhost/api/xmlrpc')
    >>> service
    <ServerProxy for localhost/api/xmlrpc>
    >>> with patch.object(XMLRPCCookieAuthTransport, 'request') as proxy:
    ...     response = service.get()
