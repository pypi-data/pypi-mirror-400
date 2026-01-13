
===========================
PyAMS HTTP protocol helpers
===========================

PyAMS provides a few helpers to handle HTTP protocol, and mainly to handle HTTP proxies:

    >>> from unittest.mock import patch
    >>> from pyams_utils.protocol.http import get_client, get_client_from_url

    >>> client = get_client('GET', 'http', 'localhost:18081', '/', {'query': 1})
    >>> with patch('httplib2.Http.request', return_value=(200, 'OK')):
    ...     client.get_response()
    (200, 'OK')

    >>> client = get_client_from_url('http://localhost/',
    ...                              credentials=('login', 'password'),
    ...                              proxy=('localhost', 18081),
    ...                              proxy_auth=('proxy_user', 'proxy_password'))
    >>> with patch('httplib2.Http.request', return_value=(200, 'OK')):
    ...     client.get_response()
    (200, 'OK')


This module also provides classes to handle HTTP proxies info:

    >>> from pyams_utils.protocol.http import ProxyInfo
    >>> info = ProxyInfo()

    >>> bool(info)
    False
    >>> info.get_proxy_url(None) is None
    True

    >>> from pyams_utils.request import check_request
    >>> request = check_request()
    >>> info.get_proxy_url(request) is None
    True

    >>> info.host = 'proxy.example.com'
    >>> info.get_proxy_url(request)
    'http://proxy.example.com:8080/'

    >>> info.username = 'proxyuser'
    >>> info.password = 'proxypass'
    >>> info.get_proxy_url(request)
    'http://proxyuser:proxypass@proxy.example.com:8080/'
