
=============================
PyAMS_utils traversing module
=============================

Traversing is a common concept in web applications, which consists in going from parent to
child based on request elements.


Basic traversal management
--------------------------

For this to work, we have to now which is the parent of a given object, and this object have
to know which are it's childs.

    >>> import pprint

    >>> from pyramid.testing import setUp, tearDown
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

    >>> import transaction
    >>> from pyams_utils.zodb import ZODBConnection
    >>> from pyams_utils.tests import IMyFolder, MyFolder

    >>> conn = ZODBConnection()
    >>> root = conn.get_connection().root()
    >>> parent = root['application'] = MyFolder()
    >>> child = MyFolder()
    >>> parent['child'] = child
    >>> 'child' in parent
    True
    >>> child.__parent__ is parent
    True

    >>> from pyams_utils.traversing import get_name, get_parent
    >>> get_name(child)
    'child'

The "get_parent" function can be used to get parents of an object; by default, it returns any
object (including the context object itself) which implements an interface, or for which an
interface adapter is available:

    >>> get_parent(child) is child
    True

You can add a parameter to exclude context from search:

    >>> get_parent(child, allow_context=False) is parent
    True

You can also add a parameter to define a custom interface which searched object should implement,
or for which an adapter is available:

    >>> get_parent(child, IMyFolder, allow_context=False) is parent
    True

You can also set a condition, which is a function which may return True when applied on an object;
this condition is checked only if defined interface is implemented or adapted:

    >>> parent.name = 'Parent name'
    >>> get_parent(child, condition=lambda x: x.name.startswith('Parent')) is parent
    True


PyAMS namespace traverser
-------------------------

PyAMS provides a custom traverser called **NamespaceTraverser**; in addition to standard traverser
provided by Pyramid, this traverser allows to define custom "traversing namespaces", which can be
defined as adapters to *ITraversable* interface:

    >>> from pyramid.testing import DummyRequest
    >>> from pyams_utils.traversing import NamespaceTraverser

    >>> traverser = NamespaceTraverser(parent)

    >>> request = DummyRequest(path='/', matchdict=None)
    >>> result = traverser(request)
    >>> pprint.pprint(result)
    {'context': <...MyFolder object at 0x...>,
     'root': <...MyFolder object at 0x...>,
     'subpath': (),
     'traversed': (),
     'view_name': '',
     'virtual_root': <...MyFolder object at 0x...>,
     'virtual_root_path': ()}
    >>> result['root'] is parent
    True
    >>> result['virtual_root'] is parent
    True
    >>> result['context'] is parent
    True

    >>> request = DummyRequest(path='/child/index.html', matchdict=None)
    >>> result = traverser(request)
    >>> pprint.pprint(result)
    {'context': <....MyFolder object at 0x...>,
     'root': <...MyFolder object at 0x...>,
     'subpath': (),
     'traversed': ('child',),
     'view_name': 'index.html',
     'virtual_root': <...MyFolder object at 0x...>,
     'virtual_root_path': ()}
    >>> result['root'] is parent
    True
    >>> result['virtual_root'] is parent
    True
    >>> result['context'] is child
    True

Let's try to add a sub-child:

    >>> subchild = MyFolder()
    >>> child['subchild'] = subchild
    >>> transaction.commit()

    >>> request = DummyRequest(path='/child/subchild/index.html', matchdict=None)
    >>> result = traverser(request)
    >>> pprint.pprint(result)
    {'context': <....MyFolder object at 0x...>,
     'root': <...MyFolder object at 0x...>,
     'subpath': (),
     'traversed': ('child', 'subchild'),
     'view_name': 'index.html',
     'virtual_root': <...MyFolder object at 0x...>,
     'virtual_root_path': ()}
    >>> result['root'] is parent
    True
    >>> result['virtual_root'] is parent
    True
    >>> result['context'] is subchild
    True

Traversing namespaces are used by using a "++" in the URL, followed by the traversing adapter
name which should be used; the *traverse* method should return an object, which will be the base
of the following URL traversing; in some cases, some traversers can just update the initial
context or request, and return the initial context:

    >>> request = DummyRequest(path='/++test++/index.html', matchdict=None)
    >>> result = traverser(request)
    Traceback (most recent call last):
    ...
    pyramid.httpexceptions.HTTPNotFound: The resource could not be found.

    >>> from pyams_utils.adapter import ContextAdapter
    >>> class TestTraverser(ContextAdapter):
    ...     def traverse(self, name, further=None):
    ...         return self.context.value

    >>> from zope.traversing.interfaces import ITraversable
    >>> config.registry.registerAdapter(TestTraverser, (IMyFolder,), ITraversable, name='test')

    >>> request = DummyRequest(path='/++test++/index.html', matchdict=None)
    >>> result = traverser(request)
    >>> pprint.pprint(result)
    {'context': <object object at 0x...>,
     'root': <...MyFolder object at 0x...>,
     'subpath': (),
     'traversed': ('++test++',),
     'view_name': 'index.html',
     'virtual_root': <...MyFolder object at 0x...>,
     'virtual_root_path': ()}
    >>> result['root'] is parent
    True
    >>> result['virtual_root'] is parent
    True
    >>> result['context'] is parent.value
    True

Note here that the "name" argument is optional; if a value is present after the second "++"
character in the URL, it is this value that is given as parameter to the *traverse* method:

    >>> class AttrTraverser(ContextAdapter):
    ...     def traverse(self, name, further=None):
    ...         return getattr(self.context, name)

    >>> config.registry.registerAdapter(TestTraverser, (IMyFolder,), ITraversable, name='attr')

    >>> request = DummyRequest(path='/++attr++value/index.html', matchdict=None)
    >>> result = traverser(request)
    >>> pprint.pprint(result)
    {'context': <object object at 0x...>,
     'root': <...MyFolder object at 0x...>,
     'subpath': (),
     'traversed': ('++attr++value',),
     'view_name': 'index.html',
     'virtual_root': <...MyFolder object at 0x...>,
     'virtual_root_path': ()}
    >>> result['root'] is parent
    True
    >>> result['virtual_root'] is parent
    True
    >>> result['context'] is parent.value
    True


Custom "+" traverser
--------------------

PyAMS support a custom traverser called "+", which allows to get short URLs in it's content
management package (See "PyAMS_content" package):

    >>> request = DummyRequest(path='/+/123', matchdict=None)
    >>> result = traverser(request)
    Traceback (most recent call last):
    ...
    pyramid.httpexceptions.HTTPNotFound: The resource could not be found.

You need to create a custom traverse adapter called "+":

    >>> from pyramid.httpexceptions import HTTPNotFound
    >>> from pyams_utils.adapter import ContextRequestAdapter

    >>> class PlusTraverser(ContextRequestAdapter):
    ...     def traverse(self, name, furtherpath=None):
    ...         if name == "subchild":
    ...             return subchild
    ...         raise HTTPNotFound

    >>> from zope.traversing.interfaces import ITraversable
    >>> config.registry.registerAdapter(PlusTraverser,
    ...                                 required=(object, DummyRequest),
    ...                                 provided=ITraversable,
    ...                                 name='+')

    >>> result = traverser(request)
    Traceback (most recent call last):
    ...
    pyramid.httpexceptions.HTTPNotFound: The resource could not be found.

    >>> request = DummyRequest(path='/+', matchdict=None)
    >>> result = traverser(request)
    Traceback (most recent call last):
    ...
    pyramid.httpexceptions.HTTPNotFound: The resource could not be found.

    >>> request = DummyRequest(path='/+/subchild', matchdict=None)
    >>> result = traverser(request)
    >>> pprint.pprint(result)
    {'context': <...MyFolder object at 0x...>,
     'root': <...MyFolder object at 0x...>,
     'subpath': (),
     'traversed': ('+', 'subchild'),
     'view_name': '',
     'virtual_root': <...MyFolder object at 0x...>,
     'virtual_root_path': ()}
    >>> result['root'] is parent
    True
    >>> result['virtual_root'] is parent
    True
    >>> result['context'] is subchild
    True


Traverser should handle virtual host correctly:

    >>> request = DummyRequest(path='/child/index.html',
    ...                        environ={'HTTP_X_VHM_ROOT': '/vhost'})
    >>> result = traverser(request)
    >>> pprint.pprint(result)
    {'context': <...MyFolder object at 0x...>,
     'root': <...MyFolder object at 0x...>,
     'subpath': (),
     'traversed': ('vhost',),
     'view_name': 'vhost',
     'virtual_root': <...MyFolder object at 0x...>,
     'virtual_root_path': ('vhost',)}
    >>> result['root'] is parent
    True
    >>> result['virtual_root'] is parent
    True
    >>> result['context'] is parent
    True


Getting context parents
-----------------------

Functions are available to get parents from a given object.

    >>> from pyams_utils.traversing import get_parent, get_parents_until

    >>> get_parent(child, IMyFolder) is child
    True
    >>> get_parent(child, IMyFolder, allow_context=False) is parent
    True

You can also set a condition on first returned item:

    >>> get_parent(subchild, IMyFolder, condition=lambda x: len(x) != 0) is child
    True

Trying to get a missing parent just returns a null value or an empty list:

    >>> from zope.interface import Interface
    >>> class ICustom(Interface):
    ...     """Custom interface"""

    >>> get_parent(subchild, ICustom) is None
    True

You can also get all parents until a parent with given interface is found:

    >>> list(get_parents_until(subchild, IMyFolder)) == list([subchild])
    True
    >>> list(get_parents_until(subchild, IMyFolder, allow_context=False)) == list([child])
    True
    >>> list(get_parents_until(subchild, IMyFolder, condition=lambda x: len(x) != 0)) == list([subchild, child])
    True

Getting parents until missing parent interface returns all parents:

    >>> list(get_parents_until(subchild, ICustom)) == list([subchild, child, parent])
    True


Context path elements
---------------------

Getting path elements can be used to index all parents of a given element; this allows, for
example, to add a "container" criteria to a catalog query to search only objects which are
contained into a given container:

    >>> from pyams_utils.traversing import PathElementsAdapter
    >>> adapter = PathElementsAdapter(subchild)
    >>> len(adapter.parents)
    0

    >>> from zope.intid.interfaces import IIntIds
    >>> from zope.intid import IntIds

    >>> intids = IntIds()
    >>> config.registry.registerUtility(intids, IIntIds)

    >>> parents = adapter.parents
    >>> len(parents)
    3
    >>> intids.queryId(subchild) in parents
    True
    >>> intids.queryId(child) in parents
    True
    >>> intids.queryId(parent) in parents
    True


Tests cleanup:

    >>> tearDown()
