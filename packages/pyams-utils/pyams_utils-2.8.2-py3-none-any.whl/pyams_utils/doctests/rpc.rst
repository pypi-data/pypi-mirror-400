
======================
PyAMS_utils rpc module
======================

This small module is used to handle RPC exceptions.

JSON-RPC and XML-RPC use distinct exceptions classes, but both of them provide the same
set of application specific error codes.

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)

    >>> from pyams_utils.rpc import raise_rpc_exception, RPC_FORBIDDEN

    >>> request = DummyRequest(content_type='text/xml')
    >>> raise_rpc_exception(request, RPC_FORBIDDEN)
    Traceback (most recent call last):
    ...
    pyams_utils.rpc.XmlRpcForbidden: <XmlRpcForbidden None: 'forbidden'>

    >>> request = DummyRequest(content_type='application/json')
    >>> raise_rpc_exception(request, RPC_FORBIDDEN)
    Traceback (most recent call last):
    ...
    pyams_utils.rpc.JsonRpcForbidden

You can add optional message and data arguments when calling the helper function:

    >>> request = DummyRequest(content_type='text/xml')
    >>> raise_rpc_exception(request, RPC_FORBIDDEN, message="alternative message", data={'context': 'My context'})
    Traceback (most recent call last):
    ...
    pyams_utils.rpc.XmlRpcForbidden: <XmlRpcForbidden None: 'alternative message'>

    >>> request = DummyRequest(content_type='application/json')
    >>> exc = None
    >>> try:
    ...     raise_rpc_exception(request, RPC_FORBIDDEN, message="alternative message", data={'context': 'My context'})
    ... except Exception as exc2:
    ...     exc = exc2

    >>> exc
    JsonRpcForbidden()
    >>> exc.message
    'alternative message'
    >>> exc.data
    {'context': 'My context'}


    >>> tearDown()
