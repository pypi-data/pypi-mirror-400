
============================
PyAMS_utils container module
============================

This PyAMS_utils module can be used to handle containers management:

    >>> from pyramid.testing import setUp, tearDown
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)


Simple container mixin
----------------------

The simple container class is used to handle a simple sequence inside.

    >>> from zope.container.contained import Contained
    >>> from zope.container.folder import Folder
    >>> from pyams_utils.container import SimpleContainerMixin

    >>> class SimpleContainer(SimpleContainerMixin, Folder):
    ...     """Simple container class"""

    >>> container = SimpleContainer()
    >>> bool(container.append(Contained()))
    True
    >>> bool(container.append(Contained()))
    True
    >>> len(container)
    2


BTree ordered containers
------------------------

BTree containers are generally used to handle folder-like containers, but they can't keep
order of items that were inserted into it; this container class allows to keep order on a large
set of items efficiently:

    >>> from pyams_utils.container import BTreeOrderedContainer
    >>> container = BTreeOrderedContainer()
    >>> container['item2'] = object()
    >>> container['item1'] = object()
    >>> list(container.keys())
    ['item2', 'item1']


Parent selector predicate
-------------------------

PyAMS "parent_selector" predicate allows to filter containers events based on provided
interfaces or implemention class of an event "parent" object:

    >>> from zope.interface import Interface, alsoProvides
    >>> class IMyContainer(Interface):
    ...     """Custom container marker interface"""

    >>> from pyams_utils.container import ParentSelector
    >>> selector = ParentSelector(IMyContainer, config)
    >>> selector.text()
    'parent_selector = (<InterfaceClass pyams_utils.tests.test_utilsdocs.IMyContainer>,)'

    >>> from zope.location import Location
    >>> class MyContent(Location):
    ...     """Content class"""
    >>> content = MyContent()

    >>> from zope.lifecycleevent import ObjectCreatedEvent, ObjectAddedEvent
    >>> event = ObjectCreatedEvent(content)
    >>> selector(event)
    False

    >>> container['item3'] = content
    >>> event = ObjectAddedEvent(content, container, 'item3')
    >>> selector(event)
    False

    >>> alsoProvides(container, IMyContainer)
    >>> selector(event)
    True

Parent selector can also be based on a class instead of an interface:

    >>> selector = ParentSelector(BTreeOrderedContainer, config)
    >>> selector(event)
    True


Container sublocations
----------------------

There are many situations where it's required to get access to all sublocations of a given
container; while it's quite obvious to access sub-objects when the object is a container, it
can be far more complex when these sub-objects are defined by adapters, and be stored into
annotations or anywhere else:

    >>> from zope.interface import implementer
    >>> from pyams_utils.adapter import ContextAdapter
    >>> from zope.location.interfaces import ISublocations
    >>> @implementer(ISublocations)
    ... class ContainerSublocationsAdapter(ContextAdapter):
    ...     def sublocations(self):
    ...         yield 'Value 1'
    >>> config.registry.registerAdapter(ContainerSublocationsAdapter,
    ...                                 (IMyContainer, ), ISublocations, name='Custom')

    >>> locations = config.registry.getAdapter(container, ISublocations)
    >>> list(locations.sublocations())
    ['Value 1', <object object at 0x...>, <object object at 0x...>, <....MyContent object at 0x...>]


Finding contained objects
-------------------------

The ISublocations interface allows to find all objects matching a given interface:

    >>> class IMyContent(Interface):
    ...     """Custom content marker interface"""
    >>> from pyams_utils.finder import find_objects_providing
    >>> list(find_objects_providing(container, IMyContent))
    []

    >>> alsoProvides(content, IMyContent)
    >>> list(find_objects_providing(container, IMyContent))
    [<....MyContent object at 0x...>]
    >>> list(find_objects_providing(container, IMyContent, with_depth=True))
    [(<....MyContent object at 0x...>, 1)]

You can also include root object in your results:

    >>> list(find_objects_providing(container, IMyContainer))
    [<...BTreeOrderedContainer object at 0x...>]
    >>> list(find_objects_providing(container, IMyContainer, with_depth=True))
    [(<...BTreeOrderedContainer object at 0x...>, 0)]

    >>> list(find_objects_providing(container, IMyContainer, ignore_root=True))
    []


Tests cleanup:

    >>> tearDown()
