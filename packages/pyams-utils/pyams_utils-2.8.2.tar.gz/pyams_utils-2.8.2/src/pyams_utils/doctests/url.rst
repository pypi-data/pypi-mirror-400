
======================
PyAMS_utils url module
======================

PyAMS provides several helpers which can be used to generate several kinds of URLs:
 - absolute URLs
 - canonical URLs
 - relative URLs

For all these kinds of URLs, a function is available as well as a TALES extension.

    >>> import pprint

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)
    >>> config.registry.settings['zodbconn.uri'] = 'memory://'

    >>> from pyramid_zodbconn import includeme as include_zodbconn
    >>> include_zodbconn(config)
    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)


Absolute URls
-------------

Absolute URLs are classical URLs, which allows to define a "physical" path to any located object:

    >>> import transaction
    >>> from pyams_utils.zodb import ZODBConnection
    >>> conn = ZODBConnection()

    >>> from pyams_utils.url import absolute_url, AbsoluteUrlTalesExtension

    >>> from pyams_utils.tests import MyTestContent
    >>> with conn as root:
    ...     root.__name__ = ''
    ...     content = root['MyContent'] = MyTestContent()
    ...     content.__name__ = 'MyContent'
    ...     content.__parent__ = root
    ...     transaction.commit()

    >>> request = DummyRequest()
    >>> pprint.pprint((absolute_url(content, request),
    ...                absolute_url(content, request, 'index.html'),
    ...                absolute_url(content, request, '#index.html'),
    ...                absolute_url(content, request, 'index.html', 'query=1'),
    ...                absolute_url(content, request, 'index.html', {'query': 1})))
    ('http://example.com/MyContent',
     'http://example.com/MyContent/index.html',
     'http://example.com/MyContent#index.html',
     'http://example.com/MyContent/index.html?query=1',
     'http://example.com/MyContent/index.html?query=1')

    >>> extension = AbsoluteUrlTalesExtension(content, request, None)
    >>> extension.render()
    'http://example.com/MyContent'

Getting a string URL just returns the initial string:

    >>> absolute_url('My string', request)
    'My string'


Canonical URLs
--------------

Canonical URL's generator relies on an optional ICanonicalURL multi-adapter. By default,
canonical URLs are identical to absolute URLs:

    >>> from pyams_utils.url import canonical_url, CanonicalUrlTalesExtension
    >>> pprint.pprint(canonical_url(content, request))
    'http://example.com/MyContent'

We can provide a custom adapter to ICanonicalURL:

    >>> from pyramid.interfaces import IRequest
    >>> from pyams_utils.interfaces.url import ICanonicalURL
    >>> from pyams_utils.adapter import ContextRequestAdapter
    >>> class CanonicalUrlAdapter(ContextRequestAdapter):
    ...     def get_url(self, view_name, query):
    ...         return '{}/my_canonical_url'.format(absolute_url(self.context, self.request))
    >>> config.registry.registerAdapter(CanonicalUrlAdapter, (MyTestContent, IRequest),
    ...                                 ICanonicalURL)

    >>> pprint.pprint(canonical_url(content, request))
    'http://example.com/MyContent/my_canonical_url'

    >>> extension = CanonicalUrlTalesExtension(content, request, None)
    >>> extension.render()
    'http://example.com/MyContent/my_canonical_url'

Getting a string URL just returns the initial string:

    >>> canonical_url('My string', request)
    'My string'


Relative URLs
-------------

Relative URLs can be used when you need to get an object URL relatively to another context,
which is called a "display" context.
Relative URLs generator relies on an optional IRelativeURL multi-adapter. By default,
relative URLs are identical to absolute URLs:

    >>> from zope.annotation.interfaces import IAttributeAnnotatable, IAnnotations
    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> config.registry.registerAdapter(AttributeAnnotations, (IAttributeAnnotatable, ), IAnnotations)

    >>> from pyams_utils.url import relative_url, RelativeUrlTalesExtension
    >>> pprint.pprint(relative_url(content, request))
    'http://example.com/MyContent'

We can provide a custom adapter to IRelativeURL:

    >>> from pyams_utils.interfaces.url import IRelativeURL
    >>> from pyams_utils.adapter import ContextRequestAdapter
    >>> class RelativeUrlAdapter(ContextRequestAdapter):
    ...     def get_url(self, display_context, view_name, query):
    ...         return '{}/my_relative_url'.format(absolute_url(self.context, self.request))
    >>> config.registry.registerAdapter(RelativeUrlAdapter, (MyTestContent, IRequest),
    ...                                 IRelativeURL)

    >>> pprint.pprint(relative_url(content, request))
    'http://example.com/MyContent/my_relative_url'

    >>> extension = RelativeUrlTalesExtension(content, request, None)
    >>> extension.render()
    'http://example.com/MyContent/my_relative_url'


Tests cleanup:

    >>> tearDown()
