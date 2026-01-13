
==========================
PyAMS_utils factory module
==========================

By registering their own objects factories, extension packages can easily provide their
own implementation of any PyAMS interface handled by factories.

Instead of directly using a class as an object factory, the object of this module is to
let you create an object based on an interface. The first step is to create an object
implementing this interface, and then to register it as a factory:

    >>> from pyramid.testing import setUp, tearDown
    >>> config = setUp(hook_zca=True)

    >>> from zope.interface import Interface, implementer
    >>> class IMyInterface(Interface):
    ...     '''Custom marker interface'''

You can get an interface name:

    >>> from pyams_utils.factory import get_interface_name, get_interface_base_name

    >>> get_interface_name(IMyInterface)
    'pyams_utils.tests.test_utilsdocs.IMyInterface'
    >>> get_interface_base_name(IMyInterface)
    'IMyInterface'

    >>> @implementer(IMyInterface)
    ... class MyClass:
    ...    '''Class implementing my interface'''

    >>> from pyams_utils.factory import register_factory
    >>> register_factory(IMyInterface, MyClass)

You can also register a named factory:

    >>> register_factory(IMyInterface, MyClass, name='my-factory')

Factory registry can also be handle by a decorator called "factory_config":

    >>> from pyams_utils.factory import factory_config

    >>> @factory_config(IMyInterface)
    ... class MyClass(object):
    ...     '''Class implementing my interface'''

A class declared as factory for a specific interface automatically implements the given interface.
You can also provide a tuple or set of interfaces in "factory_config()" decorator.

When a factory is registered, you can look for a factory:

    >>> from pyams_utils.factory import get_object_factory
    >>> factory = get_object_factory(IMyInterface)
    >>> factory
    <pyams_utils.factory.register_factory.<locals>.Temp object at 0x...>
    >>> if factory is not None:
    ...     myobject = factory()
    ... else:
    ...     myobject = object()

Named factories are used in the same way:

    >>> factory = get_object_factory(IMyInterface, name='my-factory')
    >>> factory
    <pyams_utils.factory.register_factory.<locals>.Temp object at 0x...>

Getting factory from anything which isn't an interface returns the original object:

    >>> get_object_factory(None) is None
    True
    >>> get_object_factory(str) is str
    True
    >>> get_object_factory(1) == 1
    True

You can also use the *create_object* helper to create an object implementing an interface for
which a factory was registered:

    >>> from pyams_utils.factory import create_object
    >>> myobject2 = create_object(IMyInterface)
    >>> myobject2 is None
    False

If there is no registered factory for the provided interface and name, result is None:

    >>> class IAnotherInterface(Interface):
    ...     """Another interface"""

    >>> create_object(IAnotherInterface) is None
    True


Factories registry
------------------

It's sometimes required to get a list of all registered factories for a given interface:

    >>> from pprint import pprint
    >>> from pyams_utils.factory import get_all_factories

    >>> pprint(list(get_all_factories(IMyInterface)))
    [('', <class 'pyams_utils.tests.test_utilsdocs.MyClass'>),
     ('my-factory', <class 'pyams_utils.tests.test_utilsdocs.MyClass'>)]


Tests cleanup:

    >>> tearDown()
