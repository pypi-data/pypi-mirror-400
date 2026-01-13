
==========================
PyAMS_utils adapter module
==========================

Adapters are components which are used to adapt a set of "input" objects instances, implementing
interfaces, to another object implementing another interface.

A lookup is done into components registry to find an available adapter for all these interfaces.

An adapter is nothing but a simple object; it doesn't have to inherit from anything, but it's
constructor must accept as many arguments as defined into adapter's "required" parameters length.

PyAMS_utils provides a small set of commonly used adapters:

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)

    >>> from pyams_utils import adapter

    >>> context, request, view = object(), object(), object()

    >>> context_adapter = adapter.ContextAdapter(context)
    >>> context_request_adapter = adapter.ContextRequestAdapter(context, request)
    >>> context_request_view_adapter = adapter.ContextRequestViewAdapter(context, request, view)

NullAdapter is a custom adapter which can be used to undefine an adapter in a given context:

    >>> null_adapter = adapter.NullAdapter(context, request)
    >>> null_adapter is None
    True


Annotations adapters
--------------------

Sometimes, some adapters have to store informations into one or more objects that they adapt
(generally the context); instead of using internal attributes which could conflict with properties
defined by other packages, we use annotations which are store in a custom "__annotations__" mapping
attribute; a custom factory is provided by PyAMS_utils to define and get such annotations:

    >>> from zope.interface import implementer, Interface
    >>> from zope.annotation.interfaces import IAttributeAnnotatable

    >>> class IMyContext(IAttributeAnnotatable):
    ...     """My context interface"""

    >>> @implementer(IMyContext)
    ... class MyContext:
    ...     """Context object class"""

    >>> class IMyAdapter(Interface):
    ...     """Adapter interface"""

    >>> @implementer(IMyAdapter)
    ... class MyAdapter:
    ...     """Adapter class"""
    ...     weight = 1
    ...     def __init__(self):
    ...         print("Creating adapter...")

    >>> def context_adapter_factory(context):
    ...     return adapter.get_annotation_adapter(context, "my.annotations.key", MyAdapter)

Adapter registration can be done using a decorator, but we register it manually for testing:

    >>> config.registry.registerAdapter(context_adapter_factory, (IMyContext,), IMyAdapter)

    >>> context = MyContext()
    >>> adapted = IMyAdapter(context)
    Creating adapter...
    >>> IMyAdapter.providedBy(adapted)
    True
    >>> 'my.annotations.key' in context.__annotations__
    True
    >>> context.__annotations__['my.annotations.key'] is adapted
    True

When calling the same adapter several times, the annotations lookup just returns the previously
created object:

    >>> IMyAdapter(context)
    <...MyAdapter object at 0x...>

The given "factory" argument value can be a factory or an interface; if an interface is provided,
a lookup is made for a registered factory for this interface:

    >>> from pyams_utils import factory
    >>> factory.register_factory(IMyAdapter, MyAdapter, registry=config.registry)

    >>> adapted = adapter.get_annotation_adapter(context, "my.annotations.key2", IMyAdapter,
    ...                                          registry=config.registry)
    Creating adapter...
    >>> context.__annotations__['my.annotations.key2'] is adapted
    True

If 'markers' argument is provided, this is a list of new interfaces that the new created object
will provide:

    >>> class IMyMarker1(Interface):
    ...     "First marker interface"

    >>> adapted = adapter.get_annotation_adapter(context, "my.annotations.key3", IMyAdapter,
    ...                                          markers=IMyMarker1, registry=config.registry)
    Creating adapter...
    >>> IMyMarker1.providedBy(adapted)
    True

By default, the context is set as parent of the new adapting object:

    >>> adapted.__parent__ is context
    True

If "parent" is set, this object will be defined as the parent instead of the context:

You can also define a callback which will be called after object creation:

    >>> adapted = adapter.get_annotation_adapter(context, "my.annotations.key4", IMyAdapter,
    ...                                          markers=IMyMarker1, registry=config.registry,
    ...                                          callback=lambda x: print('{!r}'.format(x)))
    Creating adapter...
    <...MyAdapter object at 0x...>

You can provide a default value to an annotation adapter:

    >>> adapter.get_annotation_adapter(context, "my.annotations.key5", IMyAdapter,
    ...                                default='default value')
    'default value'

If no factory interface is provided, result is also set to None:

    >>> adapter.get_annotation_adapter(context, "my.annotations.key6") is None
    True


Of course, trying to get annotations from an object which doesn't support them will return a
None value:

    >>> context = object()
    >>> adapter.get_annotation_adapter(context, "my.annotations.key", IMyAdapter) is None
    True


Registering adapters
--------------------

Adapters can be easilly registered using a custom decorator called "adapter_config":

    >>> from pyams_utils.testing import call_decorator

    >>> class ISimpleInterface(Interface):
    ...     """Simple marker interface"""

    >>> class SimpleAdapter(adapter.ContextAdapter):
    ...     """Simple adapter"""

    >>> call_decorator(config, adapter.adapter_config, SimpleAdapter,
    ...                required=str, provided=ISimpleInterface)

    >>> ISimpleInterface('string')
    <pyams_utils.tests.test_utilsdocs.SimpleAdapter object at 0x...>

If the adapter class doesn't implements the provided interface, the registration will
automatically add the interface to class implementations:

    >>> ISimpleInterface.implementedBy(SimpleAdapter)
    True

You can avoid the "provided" argument if your adapter implements a single interface:

    >>> @implementer(ISimpleInterface)
    ... class SimpleAdapter(adapter.ContextAdapter):
    ...     """Simple adapter"""

    >>> call_decorator(config, adapter.adapter_config, SimpleAdapter, for_=int)
    >>> ISimpleInterface(42)
    <pyams_utils.tests.test_utilsdocs.SimpleAdapter object at 0x...>

    >>> @implementer(IMyAdapter, ISimpleInterface)
    ... class SimpleAdapter(adapter.ContextAdapter):
    ...     """Simple adapter"""

    >>> call_decorator(config, adapter.adapter_config, SimpleAdapter, for_=int)
    Traceback (most recent call last):
    ...
    TypeError: Missing 'provides' argument


Sorting adapters
----------------

It can be required to sort adapters based on a "weight":

    >>> call_decorator(config, adapter.adapter_config, SimpleAdapter,
    ...                required=IMyContext, provided=IMyAdapter, name='second')

    >>> context = MyContext()
    >>> sorted(config.registry.getAdapters((context,), IMyAdapter),
    ...        key=adapter.get_adapter_weight)
    Creating adapter...
    [('second', <....SimpleAdapter object at 0x...>), ('', <...MyAdapter object at 0x...>)]


Querying adapters
-----------------

PyAMS provides a small helper to do an adapter lookup; this function is trying to do
a multi-adapter lookup for context, request and view (if view is provided), then for
context and request, and finally for context only.

If context is not provided or is None, request context is used:

    >>> from pyams_utils.adapter import query_adapter

    >>> request = DummyRequest()
    >>> request.context = context
    >>> query_adapter(IMyAdapter, request, name='second')
    <...SimpleAdapter object at 0x...>


Tests cleanup:

  >>> tearDown()
