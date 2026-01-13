
======================
PyAMS fanstatic module
======================

PyAMS provides a few helpers to declare external resources as standard Fanstatic resources,
or to add custom "data" attributes to a given resource:

    >>> from pyramid.testing import setUp, tearDown
    >>> config = setUp(hook_zca=True)

    >>> from fanstatic import Library, Injector, get_needed
    >>> from fanstatic.core import set_resource_file_existence_checking

    >>> import webob
    >>> from pyams_utils import fanstatic

    >>> from pyams_utils.testing import library
    >>> set_resource_file_existence_checking(False)
    >>> x1_css = fanstatic.ResourceWithData(library, 'a.css', data={'test-value': 'nested'})
    >>> x1_js = fanstatic.ResourceWithData(library, 'a.js', data={'test-value': 'nested'}, depends=(x1_css,))
    >>> x1_img = fanstatic.ResourceWithData(library, 'a.img', data={'test-value': 'nested'}, depends=(x1_js,))
    >>> set_resource_file_existence_checking(True)

Let's try to create a custom WSGI application to test this resource:

    >>> def app(environ, start_response):
    ...     start_response('200 OK', [('Content-Type', 'text/html')])
    ...     needed = get_needed()
    ...     needed.need(x1_img)
    ...     needed.set_base_url('http://example.com')
    ...     return [b'<html><head></head><body></body></html>']

    >>> app = Injector(app)
    >>> request = webob.Request.blank('/')
    >>> response = request.get_response(app)
    >>> print(response.body.decode())
    <html><head><link rel="stylesheet" data-test-value="nested" type="text/css" href="http://example.com/fanstatic/foo/a.css" />
    <script data-test-value="nested" type="text/javascript" src="http://example.com/fanstatic/foo/a.js"></script>
    </head><body></body></html>

Let's try with an external resource now, with another app:

    >>> x2 = fanstatic.ExternalResource(library, 'http://cdn.example.com/pyams/b.js',
    ...                                 renderer=None, defer=True, depends=(x1_js,),)

    >>> def app(environ, start_response):
    ...     start_response('200 OK', [('Content-Type', 'text/html')])
    ...     needed = get_needed()
    ...     needed.need(x2)
    ...     needed.set_base_url('http://example.com')
    ...     return [b'<html><head></head><body></body></html>']

    >>> app = Injector(app)
    >>> request = webob.Request.blank('/')
    >>> response = request.get_response(app)
    >>> print(response.body.decode())
    <html><head><link rel="stylesheet" data-test-value="nested" type="text/css" href="http://example.com/fanstatic/foo/a.css" />
    <script data-test-value="nested" type="text/javascript" src="http://example.com/fanstatic/foo/a.js"></script>
    <script type="text/javascript" src="http://cdn.example.com/pyams/b.js" defer></script></head><body></body></html>

Let's try with another resource type:

    >>> x3 = fanstatic.ExternalResource(library, 'http://cdn.example.com/pyams/c.css',
    ...                                 resource_type='css', defer=False, depends=(x1_js,),)

    >>> def app(environ, start_response):
    ...     start_response('200 OK', [('Content-Type', 'text/html')])
    ...     needed = get_needed()
    ...     needed.need(x3)
    ...     needed.set_base_url('http://example.com')
    ...     return [b'<html><head></head><body></body></html>']

    >>> app = Injector(app)
    >>> request = webob.Request.blank('/')
    >>> response = request.get_response(app)
    >>> print(response.body.decode())
    <html><head><link rel="stylesheet" data-test-value="nested" type="text/css" href="http://example.com/fanstatic/foo/a.css" />
    <link rel="stylesheet" type="text/css" href="http://cdn.example.com/pyams/c.css" />
    <script data-test-value="nested" type="text/javascript" src="http://example.com/fanstatic/foo/a.js"></script></head><body></body></html>

Other resources are not supported:

    >>> x4 = fanstatic.ExternalResource(library, 'http://cdn.example.com/pyams/d.png',
    ...                                 resource_type='img')

    >>> def app(environ, start_response):
    ...     start_response('200 OK', [('Content-Type', 'text/html')])
    ...     needed = get_needed()
    ...     needed.need(x4)
    ...     needed.set_base_url('http://example.com')
    ...     return [b'<html><head></head><body></body></html>']

    >>> app = Injector(app)
    >>> request = webob.Request.blank('/')
    >>> response = request.get_response(app)
    >>> print(response.body.decode())
    <html><head></head><body></body></html>


Fanstatic TALES extensions
--------------------------

PyAMS_utils provides two extensions for TALES templates.

The first extension allows to include the path of a given resource into a template:

    >>> extension = fanstatic.FanstaticTalesExtension(None, None, None)
    >>> extension.render('pyams_utils.testing:res_x1')
    '/--static--/foo/:version:.../x1.js'

The other extension is used to "need" a given resource from a template:

    >>> extension = fanstatic.FanstaticNeededResourceTalesExtension(None, None, None)
    >>> extension.render('pyams_utils.testing:res_x1')
    ''

The extension doesn't return anything, but include the resource into needed ones. Let's check:

    >>> def app(environ, start_response):
    ...     start_response('200 OK', [('Content-Type', 'text/html')])
    ...     extension.render('pyams_utils.testing:res_x1')
    ...     return [b'<html><head></head><body></body></html>']

    >>> app = Injector(app)
    >>> request = webob.Request.blank('/')
    >>> response = request.get_response(app)
    >>> print(response.body.decode())
    <html><head><script type="text/javascript" src="/fanstatic/foo/x1.js"></script></head><body></body></html>


Manual inclusion of Fanstatic resources
---------------------------------------

It's sometimes necessary to inject Fanstatic resources into an already existing HTML content, for example to
create an HTML email message. PyAMS provides an helper function for this:

    >>> from pyams_utils.fanstatic import inject_resources

    >>> def app():
    ...     needed = get_needed()
    ...     needed.need(x1_css)
    ...     return b'<html><head></head><body></body></html>'

    >>> from pyams_utils.request import create_request

    >>> request = create_request()
    >>> inject_resources(request, config.registry, app)
    '<html><head><link rel="stylesheet" data-test-value="nested" type="text/css" href="http://localhost/fanstatic/foo/a.css" /></head><body></body></html>'

    >>> tearDown()
