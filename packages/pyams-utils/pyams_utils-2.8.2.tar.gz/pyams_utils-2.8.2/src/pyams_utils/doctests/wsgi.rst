
=======================
PyAMS_utils wsgi module
=======================

The "wsgi_environ_cache" can be used to cache a method result into request environment:

    >>> import pprint

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)

    >>> from pyams_utils.wsgi import wsgi_environ_cache
    >>> class MyUtility:
    ...
    ...     @wsgi_environ_cache('MyKey')
    ...     def get_value(self, request):
    ...         pprint.pprint("Getting value...")
    ...         return 1
    ...
    ...     @wsgi_environ_cache('MyKey 2', store_none=False)
    ...     def get_other_value(self, request):
    ...         pprint.pprint("Getting second value...")
    ...         return None

    >>> request = DummyRequest()

    >>> utility = MyUtility()
    >>> utility.get_value(request)
    'Getting value...'
    1

    >>> utility.get_value(request)
    1

    >>> request.environ.get('MyKey')
    1

    >>> utility.get_other_value(request) is None
    'Getting second value...'
    True

    >>> utility.get_other_value(request) is None
    'Getting second value...'
    True

    >>> request.environ.get('MyKey 2') is None
    True


Tests cleanup:

    >>> tearDown()
