
=======================
PyAMS utils rest module
=======================

PyAMS is using Cornice with a Swagger extension which allows to provide a documentation
for all REST APIs.

This module provides a single view which is used to render OpenAPI specification of all REST
API:

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)


CORS requests handler
---------------------

REST module provides a small handler for CORS requests; this handler relies on a request adapter
to ICORSRequestHandler:

    >>> from pyams_utils.rest import handle_cors_headers

    >>> request = DummyRequest('/__api__',
    ...                        method='OPTIONS',
    ...                        headers={
    ...                            'Access-Control-Request-Headers': 'Authorization',
    ...                            'Access-Control-Request-Method': 'GET'
    ...                        })
    >>> handle_cors_headers(request)
    >>> sorted(request.response.headers)
    ['Access-Control-Allow-Credentials', 'Access-Control-Allow-Headers',
     'Access-Control-Allow-Origin', 'Content-Length', 'Content-Type']

If you service is not based on Cornice, you can provide the list of supported methods:

    >>> handle_cors_headers(request, allowed_methods=('GET', 'OPTIONS'))
    >>> sorted(request.response.headers)
    ['Access-Control-Allow-Credentials', 'Access-Control-Allow-Headers',
     'Access-Control-Allow-Methods', 'Access-Control-Allow-Origin',
     'Content-Length', 'Content-Type']
    >>> request.response.headers['Access-Control-Allow-Methods']
    'GET, OPTIONS'


Tests cleanup:

    >>> tearDown()
