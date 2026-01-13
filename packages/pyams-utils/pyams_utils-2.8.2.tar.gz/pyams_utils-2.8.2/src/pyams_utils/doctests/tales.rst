
========================
PyAMS_utils tales module
========================

PyAMS_utils provides a custom TALES expression, called "tales", which allows to use custom
TALES "extensions"; these extensions are custom single or multi-adapters to ITALESExtension
interface and can be used from Chameleon templates:

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)

    >>> from pyramid.renderers import render
    >>> from pyramid_chameleon.zpt import renderer_factory
    >>> config.add_renderer('.pt', renderer_factory)

    >>> import os, tempfile
    >>> temp_dir = tempfile.mkdtemp()

    >>> template = os.path.join(temp_dir, 'tales.pt')


Defining simple TALES extensions
--------------------------------

TALES extensions are adapters to ITALESExtension interface; they can adapt a context, a context
and a request, or a context, a request and a view.

    >>> from zope.interface import Attribute, Interface, implementer
    >>> from pyams_utils.testing import call_decorator
    >>> from pyams_utils.adapter import adapter_config, ContextAdapter, ContextRequestAdapter, \
    ...     ContextRequestViewAdapter
    >>> from pyams_utils.interfaces.tales import ITALESExtension

    >>> class BaseTALESAdapter(ContextAdapter):
    ...     def render(self, context=None):
    ...         return 'Static text'

    >>> with open(template, 'w') as file:
    ...     _ = file.write('<div>${tales:test1}</div>')

Calling for un unregistered TALES extension just returns an empty string:

    >>> render(template, {})
    '<div></div>'

We are now registering our first TALES extension:

    >>> call_decorator(config, adapter_config, BaseTALESAdapter,
    ...                name='test1', required=Interface, provides=ITALESExtension)

    >>> render(template, {})
    '<div>Static text</div>'


Defining TALES extensions with arguments
----------------------------------------

Let's now create a more complex TALES extension which is requiring arguments:

    >>> class IMyInterface(Interface):
    ...     title = Attribute("Title")

    >>> class AdvancedTALESAdapter(ContextRequestAdapter):
    ...     def render(self, context=None, prefix=''):
    ...         if context is None:
    ...             context = self.request.context
    ...         return '{}{}'.format(prefix, context.title)

    >>> call_decorator(config, adapter_config, AdvancedTALESAdapter,
    ...                name='test2', required=(IMyInterface, Interface), provides=ITALESExtension)

    >>> template = os.path.join(temp_dir, 'tales-test2.pt')
    >>> with open(template, 'w') as file:
    ...     _ = file.write("""<div tal:define="prefix 'Hello, '">${tales:test2(context, prefix)}!</div>""")

    >>> @implementer(IMyInterface)
    ... class MyContent:
    ...     prefix = 'Welcome, '
    ...     title = 'John Doe'

    >>> content = MyContent()
    >>> request = DummyRequest(context=content)
    >>> render(template, {'context': content, 'request': request})
    '<div>Hello, John Doe!</div>'

You can also use named arguments and dotted notation to access objects properties:

    >>> template = os.path.join(temp_dir, 'tales-test3.pt')
    >>> with open(template, 'w') as file:
    ...     _ = file.write("""<div>${tales:test2(context, prefix=context.prefix)}!</div>""")

    >>> render(template, {'context': content, 'request': request})
    '<div>Welcome, John Doe!</div>'


Tests cleanup:

    >>> tearDown()
