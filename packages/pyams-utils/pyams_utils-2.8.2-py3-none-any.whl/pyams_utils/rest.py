#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.rest module

This module provides CORS requests handlers, as well as OpenAPI
documentation for all defined Cornice REST endpoints.
"""

import enum
import sys
from cgi import FieldStorage

from colander import Date, Decimal, Enum, Invalid, Mapping, MappingSchema, SchemaNode, SchemaType, SequenceSchema, \
    String, Tuple, TupleSchema, drop, null
from cornice_swagger import CorniceSwagger
from cornice_swagger.converters.schema import ArrayTypeConverter, ObjectTypeConverter, \
    StringTypeConverter, TypeConverter
from pyramid.httpexceptions import HTTPBadRequest, HTTPForbidden, HTTPNotFound, HTTPServerError, \
    HTTPServiceUnavailable, HTTPUnauthorized
from pyramid.interfaces import IRequest

from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.rest import ICORSRequestHandler

__docformat__ = 'restructuredtext'

from pyams_utils import _


#
# CORS handlers
#

@adapter_config(required=IRequest,
                provides=ICORSRequestHandler)
class CORSRequestHandler:
    """Base CORS request handler"""

    def __init__(self, request):
        self.request = request

    def handle_request(self, allowed_methods=None):
        """Add requested headers to current request"""
        request = self.request
        req_headers = request.headers
        resp_headers = request.response.headers
        resp_headers['Access-Control-Allow-Credentials'] = 'true'
        resp_headers['Access-Control-Allow-Origin'] = \
            req_headers.get('Origin', request.host_url)
        if 'Access-Control-Request-Headers' in req_headers:
            headers = set(map(str.lower,
                              filter(str.__len__,
                                     map(str.strip,
                                         req_headers['Access-Control-Request-Headers'].split(','))))) \
                      | {'origin'}
            resp_headers['Access-Control-Allow-Headers'] = ', '.join(headers)
        if 'Access-Control-Request-Method' in req_headers:
            try:
                service = request.current_service
                resp_headers['Access-Control-Allow-Methods'] = \
                    ', '.join(service.cors_supported_methods)
            except AttributeError as exc:
                if allowed_methods:
                    resp_headers['Access-Control-Allow-Methods'] = ', '.join(allowed_methods)
                else:
                    test_mode = sys.argv[-1].endswith('/test')
                    if not test_mode:
                        raise HTTPServerError from exc


def handle_cors_headers(request, allowed_methods=None):
    """Handle CORS headers on REST service

    :param request: original request
    :param allowed_methods: list, tuple or set of allowed HTTP methods; if None, list of
        allowed methods will be extracted from Cornice service handlers.
    """
    handler = ICORSRequestHandler(request, None)
    if handler is not None:
        handler.handle_request(allowed_methods)


#
# Colander schemas and converters
#

class STATUS(enum.Enum):
    """Base response status enumeration"""
    SUCCESS = 'success'
    ERROR = 'error'


class BaseStatusSchema(MappingSchema):
    """Base status schema"""
    status = SchemaNode(Enum(STATUS),
                        description="Response status",
                        missing=drop)


class BaseResponseSchema(BaseStatusSchema):
    """Base response schema"""
    message = SchemaNode(String(),
                         description="Error or status message",
                         missing=drop)


class BaseResponse(MappingSchema):
    """Base response"""
    body = BaseResponseSchema()


class EnumTypeConverter(TypeConverter):
    """Enum type converter"""

    type = 'string'

    def convert_type(self, schema_node):
        """Enum type converter"""
        converted = super().convert_type(schema_node)
        converted['enum'] = list(map(lambda x: x.value,
                                     schema_node.typ.values.values()))
        return converted


class StringArraySchema(SchemaType):
    """Array or comma separated string schema field"""

    def __init__(self, separator=','):
        self.separator = separator

    @staticmethod
    def serialize(node, appstruct):
        """String array serializer"""
        return appstruct

    def deserialize(self, node, cstruct):
        """String array deserializer"""
        if cstruct is null:
            return null
        if isinstance(cstruct, str):
            return cstruct.split(self.separator)
        if isinstance(cstruct, list):
            return list(filter(str.__len__, cstruct))
        raise Invalid(node, _("${node} must be a string or an array of strings",
                              mapping={'node': node.name}))


class StringArrayTypeConverter(StringTypeConverter):
    """String array type converter"""


class StringListSchema(SequenceSchema):
    """Strings list schema field"""
    value = SchemaNode(String(),
                       description="String item value",
                       missing=drop)


class StringListTypeConverter(ArrayTypeConverter):
    """Strings list type converter"""


class PropertiesMapping(Mapping):
    """Properties schema"""

    name = 'properties'

    def serialize(self, node, appstruct):
        if appstruct is null:
            return {}
        return appstruct

    def deserialize(self, node, cstruct):
        return cstruct


class PropertiesMappingTypeConverter(ObjectTypeConverter):
    """Properties mapping type converter"""


class DecimalTypeConverter(TypeConverter):
    """Decimal type converter"""

    type = 'number'

    def convert_type(self, schema_node):
        """Decimal type converter"""
        converted = super().convert_type(schema_node)
        converted['type'] = 'number'
        return converted
    
    
class DateRangeSchema(TupleSchema):
    """Dates range schema type"""
    after = SchemaNode(Date(),
                       description="Range beginning date",
                       missing=null)
    before = SchemaNode(Date(),
                        description="Range ending date (excluded)",
                        missing=null)


class DateRangeTypeConverter(ArrayTypeConverter):
    """Date range type converter"""


class FileUploadType(String):
    """File upload type

    This type accepts FieldStorage from form-data post, or base64 encoded JSON.
    """

    def deserialize(self, node, cstruct):
        """File upload deserializer"""
        if isinstance(cstruct, FieldStorage):
            return cstruct
        return super().deserialize(node, cstruct)


class FileUploadTypeConverter(StringTypeConverter):
    """File upload type converter"""


class ObjectUploadType(String):
    """Object upload type

    This type accepts FieldStorage value from form-data post, a base64 encoded JSON value,
    or raw JSON content provided as dict
    """

    def deserialize(self, node, cstruct):
        """Object data deserializer"""
        if isinstance(cstruct, FieldStorage):
            return cstruct
        if isinstance(cstruct, dict):
            return cstruct
        return super().deserialize(node, cstruct)


class ObjectUploadTypeConverter(StringTypeConverter):
    """Object upload type converter"""


# update Cornice-Swagger types converters
CorniceSwagger.custom_type_converters.update({
    Enum: EnumTypeConverter,
    Tuple: ArrayTypeConverter,
    StringArraySchema: StringArrayTypeConverter,
    StringListSchema: StringListTypeConverter,
    PropertiesMapping: PropertiesMappingTypeConverter,
    Decimal: DecimalTypeConverter,
    DateRangeSchema: DateRangeTypeConverter,
    FileUploadType: FileUploadTypeConverter,
    ObjectUploadType: ObjectUploadTypeConverter
})


rest_responses = {
    HTTPNotFound.code: BaseResponse(description=HTTPNotFound.title),
    HTTPUnauthorized.code: BaseResponse(description=HTTPUnauthorized.title),
    HTTPForbidden.code: BaseResponse(description=HTTPForbidden.title),
    HTTPBadRequest.code: BaseResponse(description=HTTPBadRequest.title),
    HTTPServiceUnavailable.code: BaseResponse(description=HTTPServiceUnavailable.title)
}


def http_error(request, error, message=None):
    """HTTP error response"""
    request.response.status_code = error.code
    return {
        'status': STATUS.ERROR.value,
        'message': f'{error.title}: {message}' if message else error.title
    }
