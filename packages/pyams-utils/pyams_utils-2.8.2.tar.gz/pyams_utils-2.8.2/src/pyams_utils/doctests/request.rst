
==========================
PyAMS_utils request module
==========================

PyAMS_utils package provides some useful functions to handle requests.

The "check_request" function can be used when you have to be sure that a request is active in
the current execution thread; if no "real" request is active, a new one is created:

    >>> import pprint

    >>> from pyramid.testing import setUp, tearDown
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)

    >>> from pyams_utils.request import PyAMSRequest, query_request, check_request
    >>> request = query_request()
    >>> request is None
    True
    >>> request = check_request()
    >>> request
    <PyAMSRequest at ... GET http://localhost/>

    >>> request2 = check_request(principal_id='admin:admin')
    >>> request2 is request
    False

If a new request is created "from scratch", it's registry is assigned to global registry:

    >>> request.registry
    <Registry testing>

A request context can be used to activate a request into execution thread:

    >>> from pyramid.threadlocal import RequestContext
    >>> with RequestContext(request) as context_request:
    ...     context_request is request
    True
    >>> with RequestContext(request):
    ...     context_request = check_request()
    ...     context_request is request
    True

Requests can now support annotations to set and retrieve any information to a given request:

    >>> from zope.annotation.interfaces import IAttributeAnnotatable, IAnnotations
    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> config.registry.registerAdapter(AttributeAnnotations, (IAttributeAnnotatable, ), IAnnotations)

    >>> from pyams_utils.request import get_request_data, set_request_data
    >>> set_request_data(request, 'test', 'This is request data')
    >>> get_request_data(request, 'test')
    'This is request data'

Annotations can be used to automatically reify a given property into request annotations:

    >>> from pyams_utils.request import request_property
    >>> class RequestPropertyTestClass(object):
    ...
    ...     @request_property(key='My property')
    ...     def my_property(self):
    ...         print("This is my property")
    ...         return 1
    ...
    ...     @request_property()
    ...     def my_other_property(self, option=2):
    ...         print("This is another property")
    ...         return option
    ...
    >>> with RequestContext(request):
    ...     instance = RequestPropertyTestClass()
    ...     pprint.pprint((instance.my_property(),
    ...                    instance.my_other_property(),
    ...                    instance.my_other_property(20),
    ...                    instance.my_other_property(option=30)))
    This is my property
    This is another property
    This is another property
    This is another property
    (1, 2, 20, 30)

    >>> from pyams_utils.request import get_annotations
    >>> sorted(get_annotations(request).keys())
    ['My property', 'my_other_property::...', 'test']

As property value is cached into request annotations, other property calls will just return
cached value:

    >>> with RequestContext(request):
    ...     instance.my_property()
    1
    >>> with RequestContext(request):
    ...     pprint.pprint((instance.my_property(),
    ...                    instance.my_other_property()))
    (1, 2)

You can also provide a function to get annotations key:

    >>> def get_key(context, request, option=3):
    ...     return '{}::{}'.format(request.environ.get('USER_ID') or 'unknown', option)

    >>> class AnotherRequestPropertyTestClass(object):
    ...
    ...     @request_property(get_key)
    ...     def get_value(self, option=3):
    ...         print("Getting value...")
    ...         return option

    >>> with RequestContext(request):
    ...     instance = AnotherRequestPropertyTestClass()
    ...     print(instance.get_value())
    Getting value...
    3

    >>> with RequestContext(request):
    ...     instance = AnotherRequestPropertyTestClass()
    ...     print(instance.get_value(option=5))
    Getting value...
    5

    >>> sorted(get_annotations(request).keys())
    ['My property', 'my_other_property::...', 'test', 'unknown::3', 'unknown::5']

The "copy_request" function  is used to clone another request. All request methods and properties
defined via "add_request_method()" are kept, as "registry" and "root" attributes:

    >>> from pyams_utils.request import copy_request
    >>> request2 = copy_request(request)
    >>> request2.registry is request.registry
    True
    >>> request2.root is None
    True


Using request selector
----------------------

"request_selector" is a custom predicate which can be used to filter requests matching given
interface; it can be used, for example, to filter requests based on supported layers:

    >>> from zope.interface import Interface, alsoProvides
    >>> class IMyLayer(Interface):
    ...     """Custom request marker interface"""

    >>> from pyams_utils.request import RequestSelector
    >>> selector = RequestSelector(IMyLayer, config)
    >>> selector.text()
    'request_selector = (<InterfaceClass pyams_utils.tests.test_utilsdocs.IMyLayer>,)'

    >>> class RequestEvent:
    ...     def __init__(self, request):
    ...         self.request = request

    >>> event = RequestEvent(request)
    >>> selector(event)
    False

    >>> alsoProvides(request, IMyLayer)
    >>> selector(event)
    True

Request selector can also be based on a class instead of an interface:

    >>> from pyams_utils.request import PyAMSRequest
    >>> selector = RequestSelector(PyAMSRequest, config)
    >>> selector(event)
    True


Using request data
------------------

A request can store information in it's environment, but also in annotations.

    >>> from pyams_utils.request import get_request_data, set_request_data
    >>> get_request_data(request, 'mykey', 'default')
    'default'
    >>> set_request_data(request, 'mykey', 1)
    >>> get_request_data(request, 'mykey', 'default')
    1

A TALES annotation is available to get request data from Chameleon templates:

    >>> from pyams_utils.request import RequestDataExtension
    >>> extension = RequestDataExtension(object(), request, None)
    >>> extension.render('mykey')
    1


Using PyAMS request factory
---------------------------

PyAMS_utils provides a custom request factory, which defines a custom permission checker which
can be used to check roles on it's context:

    >>> from pyams_utils.request import PyAMSRequest
    >>> request = check_request()
    >>> isinstance(request, PyAMSRequest)
    True

    >>> request.context = object()
    >>> request.has_permission('View')
    <Allowed instance at ... with msg 'No security policy in use.'>

We need to define a security policy to get other ACLs:

    >>> try:
    ...     from pyams_security.policy import PyAMSSecurityPolicy
    ... except ImportError:
    ...     print('''ACLDenied permission 'View' via ACE '<default deny>' in ACL '<No ACL found on any object in resource lineage>' on context <object object at 0x...> for principals {'system.Everyone'}''')
    ... else:
    ...     config.set_security_policy(PyAMSSecurityPolicy('PyAMS secret', secure=False))
    ...     print(request.has_permission('View'))
    ACLDenied permission 'View' via ACE '<default deny>' in ACL '<No ACL found on any object in resource lineage>' on context <object object at 0x...> for principals {'system.Everyone'}

We also have a custom request factory to handle "internal" requests, this is requests which
can be used by internal services (for example by scheduled tasks):

    >>> from pyams_utils.request import INTERNAL_USER_ID, PyAMSInternalRequest
    >>> request = check_request(principal_id=INTERNAL_USER_ID)
    >>> isinstance(request, PyAMSInternalRequest)
    True


Debugging request
-----------------

This function is used for Zope compatibility:

    >>> from pyams_utils.request import get_debug
    >>> get_debug(request).showTAL
    False


Tests cleanup:

    >>> tearDown()
