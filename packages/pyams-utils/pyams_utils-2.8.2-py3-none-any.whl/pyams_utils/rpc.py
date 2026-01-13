#
# Copyright (c) 2015-2022 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.rpc module

This module defines custom exceptions and tools which can be used to handle both
standard JSON-RPC and XML-RPC exceptions.
"""

from enum import Enum

from pyramid.interfaces import IRequest
from pyramid_rpc.jsonrpc import JsonRpcError
from pyramid_rpc.xmlrpc import XmlRpcError


__docformat__ = 'restructuredtext'


RPC_SERVICE_UNAVAILABLE = 'RPC_SERVICE_UNAVAILABLE'
RPC_SERVICE_UNAVAILABLE_CODE = -32001
RPC_SERVICE_UNAVAILABLE_STR = "service unavailable"

RPC_OBJECT_NOT_FOUND = 'RPC_OBJECT_NOT_FOUND'
RPC_OBJECT_NOT_FOUND_CODE = -32002
RPC_OBJECT_NOT_FOUND_STR = "object not found"

RPC_FORBIDDEN = 'RPC_FORBIDDEN'
RPC_FORBIDDEN_CODE = -32003
RPC_FORBIDDEN_STR = "forbidden"


#
# JSON-RPC errors
#

class JsonRpcServiceUnavailable(JsonRpcError):
    """JSON-RPC service unavailable error"""
    code = RPC_SERVICE_UNAVAILABLE_CODE
    message = RPC_SERVICE_UNAVAILABLE_STR


class JsonRpcNotFound(JsonRpcError):
    """JSON-RPC not found error"""
    code = RPC_OBJECT_NOT_FOUND_CODE
    message = RPC_OBJECT_NOT_FOUND_STR


class JsonRpcForbidden(JsonRpcError):
    """JSON-RPC forbidden error"""
    code = RPC_FORBIDDEN_CODE
    message = RPC_FORBIDDEN_STR


class JsonRpcErrors(Enum):
    """JSON-RPC errors enumeration"""
    RPC_OBJECT_NOT_FOUND = JsonRpcNotFound
    RPC_SERVICE_UNAVAILABLE = JsonRpcServiceUnavailable
    RPC_FORBIDDEN = JsonRpcForbidden


#
# XML-RPC errors
#

class XmlRpcCustomError(XmlRpcError):
    """XML-RPC custom error"""

    def __init__(self, message: str = None, data=None):  # pylint: disable=unused-argument
        if message is not None:
            self.faultString = message
        super().__init__()


class XmlRpcServiceUnavailable(XmlRpcCustomError):
    """XML-RPC service unavailable error"""
    faultCode = RPC_SERVICE_UNAVAILABLE_CODE
    faultString = RPC_SERVICE_UNAVAILABLE_STR


class XmlRpcNotFound(XmlRpcCustomError):
    """XML-RPC not found error"""
    faultCode = RPC_OBJECT_NOT_FOUND_CODE
    faultString = RPC_OBJECT_NOT_FOUND_STR


class XmlRpcForbidden(XmlRpcCustomError):
    """XML-RPC forbidden error"""
    fautCode = RPC_FORBIDDEN_CODE
    faultString = RPC_FORBIDDEN_STR


class XmlRpcErrors(Enum):
    """XML-RPC errors enumeration"""
    RPC_SERVICE_UNAVAILABLE = XmlRpcServiceUnavailable
    RPC_OBJECT_NOT_FOUND = XmlRpcNotFound
    RPC_FORBIDDEN = XmlRpcForbidden


def raise_rpc_exception(request: IRequest,
                        exception_name: str,
                        message: str = None,
                        data=None):
    """Raise exception based on provided request and exception name

    This helper will check incoming request to raise appropriate exception.
    """
    if request.content_type.startswith('text/xml'):
        error = XmlRpcErrors[exception_name]
    else:
        error = JsonRpcErrors[exception_name]
    raise error.value(message=message, data=data)
