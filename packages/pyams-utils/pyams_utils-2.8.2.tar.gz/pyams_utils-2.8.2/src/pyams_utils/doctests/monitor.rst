
==========================
PyAMS_utils monitor module
==========================

The monitor module provides a REST API endpoint for monitoring the application health status.
It allows you to check the status of the application and all registered monitoring extensions.

Setting up the testing environment:

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)

    >>> from pyams_utils.monitor import MonitorExtensionStatusProperties
    >>> from pyams_utils.interfaces.monitor import IMonitorExtensionStatus


Monitor extension status
------------------------

The MonitorExtensionStatusProperties class is used to represent the status of a monitor extension.
It stores information about a specific handler including its status and an optional message:

    >>> status = MonitorExtensionStatusProperties(
    ...     handler='test.handler',
    ...     status='UP'
    ... )
    >>> status.handler
    'test.handler'
    >>> status.status
    'UP'
    >>> status.message is None
    True

You can also create a status with a message:

    >>> status_with_msg = MonitorExtensionStatusProperties(
    ...     handler='test.handler:service',
    ...     status='DOWN',
    ...     message='Service is not responding'
    ... )
    >>> status_with_msg.status
    'DOWN'
    >>> status_with_msg.message
    'Service is not responding'


Converting to dictionary
------------------------

`IMonitorExtensionStatus` interface provides a ``to_dict()`` method to convert the status to
a dictionary format suitable for JSON serialization:

    >>> status_dict = status.to_dict()
    >>> sorted(status_dict.keys())
    ['handler', 'status']
    >>> status_dict['handler']
    'test.handler'
    >>> status_dict['status']
    'UP'

When a message is present, it's included in the dictionary:

    >>> status_with_msg_dict = status_with_msg.to_dict()
    >>> sorted(status_with_msg_dict.keys())
    ['handler', 'message', 'status']
    >>> status_with_msg_dict['message']
    'Service is not responding'


Monitor API response structure
------------------------------

The monitor service returns a response with the following structure:

- `status`: Overall application status ('UP', 'DOWN', or 'PARTIAL')
- `message`: Optional message describing the status
- `services`: Optional list of extension statuses

An 'UP' status indicates all services are operational, a 'DOWN' status indicates all
services are down, and 'PARTIAL' indicates some services are down while others are up.


Creating monitor extension status via factory
----------------------------------------------

You can use the factory system to create an object providing `IMonitorExtensionStatus` interface:

    >>> from pyams_utils.factory import create_object

    >>> status_obj = create_object(IMonitorExtensionStatus,
    ...                            handler='pyams_demo.monitor:database',
    ...                            status='UP')
    >>> status_obj is not None
    True
    >>> status_obj.handler
    'pyams_demo.monitor:database'
    >>> status_obj.status
    'UP'

With a message:

    >>> error_status = create_object(IMonitorExtensionStatus,
    ...                              handler='pyams_demo.monitor:cache',
    ...                              status='DOWN',
    ...                              message='Cache server connection failed')
    >>> error_status.message
    'Cache server connection failed'
    >>> error_status.to_dict()['status']
    'DOWN'


Implementing custom monitor extensions
---------------------------------------

To create a custom monitor extension, you need to:

1. Implement the `IMonitorExtension` interface
2. Register it as a utility with the `@utility_config` decorator
3. Implement the get_status method that yields `IMonitorExtensionStatus` objects

Example of a simple monitor extension:

    >>> from zope.interface import Interface, implementer

    >>> from pyams_utils.interfaces.monitor import IMonitorExtension
    >>> from pyams_utils.registry import utility_config
    >>> from pyams_utils.testing import call_decorator

    >>> @utility_config(name='pyams_utils.testing:extension',
    ...                 provides=IMonitorExtension)
    ... class SimpleMonitorExtension:
    ...     '''Simple monitor extension for testing'''
    ...
    ...     def get_status(self, request):
    ...         yield create_object(IMonitorExtensionStatus,
    ...                             handler='pyams_utils.testing:extension',
    ...                             status='UP',
    ...                             message='Extension is operational')

    >>> call_decorator(config, utility_config, SimpleMonitorExtension, name='pyams_utils.testing:extension', provides=IMonitorExtension)

The extension yields one or more status objects that will be included in the monitor
response.


Extension status values
-----------------------

Extensions can report the following status values:

- 'UP': Service is operational
- 'DOWN': Service is not operational

    >>> valid_statuses = ['UP', 'DOWN']
    >>> 'UP' in valid_statuses
    True
    >>> 'DOWN' in valid_statuses
    True


Monitor service handler naming convention
------------------------------------------

Handler names follow a hierarchical convention using colons as separators:

- Base handler: ``package.monitor:service``
- Sub-handler: ``package.monitor:service:component``
- Detailed handler: ``package.monitor:service:component:detail``

Example handlers:

    >>> handlers = [
    ...     'pyams_content_es.monitor:client',
    ...     'pyams_content_es.monitor:indexer',
    ...     'pyams_content_es.monitor:indexer:process',
    ...     'database.monitor:connection',
    ...     'cache.monitor:redis:cluster'
    ... ]
    >>> len([h for h in handlers if h.count(':') >= 1])
    5


Monitor API endpoint
--------------------

PyAMS provides an API endpoint which can be used to get a global application monitoring status.

    >>> from pyams_utils.monitor import get_monitor_data

    >>> request = DummyRequest()
    >>> monitor_data = get_monitor_data(request)
    >>> sorted(monitor_data.keys())
    ['message', 'services', 'status']
    >>> monitor_data['status']
    'UP'
    >>> monitor_data['message']
    'All services are UP'
    >>> len(monitor_data['services'])
    1

Let's try to add another extension:

    >>> @utility_config(name='pyams_utils.testing:extension:detail',
    ...                 provides=IMonitorExtension)
    ... class SimpleMonitorDetailExtension:
    ...     '''Simple monitor detail extension for testing'''
    ...
    ...     def get_status(self, request):
    ...         yield create_object(IMonitorExtensionStatus,
    ...                             handler='pyams_utils.testing:extension:detail',
    ...                             status='DOWN',
    ...                             message='Extension is NOT operational')

    >>> call_decorator(config, utility_config, SimpleMonitorDetailExtension, name='pyams_utils.testing:extension:detail', provides=IMonitorExtension)

    >>> monitor_data = get_monitor_data(request)
    >>> monitor_data['status']
    'PARTIAL'
    >>> monitor_data['message']
    'Some services are DOWN'
    >>> len(monitor_data['services'])
    2
    >>> len(list(filter(lambda x: x['status'] == 'DOWN', monitor_data['services'])))
    1
    >>> len(list(filter(lambda x: x['status'] == 'UP', monitor_data['services'])))
    1


Tests cleanup:

    >>> tearDown()
