# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

import sys

from colander import MappingSchema, OneOf, SchemaNode, SequenceSchema, String, drop
from cornice import Service
from cornice.validators import colander_validator
from pyramid.httpexceptions import HTTPOk
from zope.schema.fieldproperty import FieldProperty

from pyams_utils.factory import create_object, factory_config
from pyams_utils.interfaces.monitor import EXTENSION_STATUS, IMonitorExtension, IMonitorExtensionStatus, \
    MONITOR_API_ROUTE, MONITOR_STATUS
from pyams_utils.rest import rest_responses

__docformat__ = 'restructuredtext'


TEST_MODE = sys.argv[-1].endswith('/test')


@factory_config(IMonitorExtensionStatus)
class MonitorExtensionStatusProperties:
    """Monitor extension status properties class"""

    handler = FieldProperty(IMonitorExtensionStatus['handler'])
    status = FieldProperty(IMonitorExtensionStatus['status'])
    message = FieldProperty(IMonitorExtensionStatus['message'])

    def __init__(self, handler, status, message=None):
        self.handler = handler
        self.status = status
        self.message = message

    def to_dict(self):
        """Get status as a dictionary"""
        result = {
            'handler': self.handler,
            'status': self.status
        }
        if self.message:
            result['message'] = self.message
        return result


#
# Monitoring service
#

monitor_service = Service(name=MONITOR_API_ROUTE,
                          pyramid_route=MONITOR_API_ROUTE,
                          description="Application monitor service")


@monitor_service.options(validators=())
def monitor_options(request):
    """Monitor service options"""
    return ''


class MonitorExtensionStatus(MappingSchema):
    """Monitor extension status"""
    handler = SchemaNode(String(),
                         description="Extension handler name")
    status = SchemaNode(String(),
                        description="Extension status",
                        validator=OneOf(EXTENSION_STATUS))
    message = SchemaNode(String(),
                         description="Extension message",
                         missing=drop)


class MonitorExtensionsList(SequenceSchema):
    """Monitor extensions list"""
    result = MonitorExtensionStatus()


class MonitorGetterResults(MappingSchema):
    """Monitor getter results"""
    status = SchemaNode(String(),
                        validator=OneOf(MONITOR_STATUS))
    message = SchemaNode(String(),
                         missing=drop)
    extensions = MonitorExtensionsList(description="List of extensions status",
                                       missing=drop)


class MonitorGetterResponse(MappingSchema):
    """Monitor getter response"""
    body = MonitorGetterResults()


monitor_get_responses = rest_responses.copy()
monitor_get_responses[HTTPOk.code] = MonitorGetterResponse(description="Monitor data")


@monitor_service.get(validators=(colander_validator),
                     response_schemas=monitor_get_responses)
def get_monitor_data(request):
    """Get monitor data"""
    try:
        _root = request.root
    except Exception as ex:
        return create_object(IMonitorExtensionStatus,
                             status='DOWN',
                             message=f"Can't get root object: {ex}")
    else:
        result = {
            'status': 'UP'
        }
        extensions = []
        for extension in request.registry.getAllUtilitiesRegisteredFor(IMonitorExtension):
            for status in extension.get_status(request):
                extensions.append(status.to_dict())
        if extensions:
            result['services'] = extensions
            has_down = any(filter(lambda x: x['status'] == 'DOWN', extensions))
            has_up = any(filter(lambda x: x['status'] == 'UP', extensions))
            if has_up and has_down:
                result['status'] = 'PARTIAL'
                result['message'] = 'Some services are DOWN'
            elif has_down:
                result['status'] = 'DOWN'
                result['message'] = 'All services are DOWN'
            else:
                result['message'] = 'All services are UP'
        return result
