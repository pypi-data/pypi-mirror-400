
==========================
PyAMS_utils session module
==========================

This module can be used to handle session data, which works nearly as request data but is
stored into session:

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)

    >>> request = DummyRequest()
    >>> request.session
    {}

    >>> from pyramid.threadlocal import manager
    >>> manager.push({'request': request, 'registry': request.registry})

    >>> from pyams_utils.session import get_session_data, set_session_data
    >>> set_session_data(request, 'app', 'key', {'key1': 'value1'})

    >>> get_session_data(request, 'app', 'key')
    {'key1': 'value1'}


Session property decorator
--------------------------

The "session_property" decorator can be used to define a property whose value is stored into
request session:

    >>> from pyams_utils.session import session_property

    >>> def get_key(instance, *args, **kwargs):
    ...     return id(instance)

    >>> class Content:
    ...
    ...     @session_property('app')
    ...     def value(self):
    ...         print("Getting property...")
    ...         return 1
    ...
    ...     @session_property('app', key='mykey')
    ...     def value2(self):
    ...         return 2
    ...
    ...     @session_property('app', key=get_key)
    ...     def value3(self):
    ...         return 3

    >>> content = Content()
    >>> content.value()
    Getting property...
    1

    >>> content.value()
    1

You can provide your own key, or a function which will be called to get the key:

    >>> content.value2()
    2

    >>> content.value3()
    3

    >>> import pprint
    >>> pprint.pprint(request.session)
    {'app::...': 3,
     'app::key': {'key1': 'value1'},
     'app::mykey': 2,
     'app::value::<pyams_utils.tests.test_utilsdocs.Content object at 0x...>': 1}


Tests cleanup:

    >>> manager.pop()
    {...}
    >>> tearDown()
