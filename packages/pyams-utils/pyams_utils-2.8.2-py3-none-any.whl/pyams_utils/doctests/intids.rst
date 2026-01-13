
=========================
PyAMS_utils intids module
=========================

IntIds are important components of many ZODB based applications, which allows to keep
unique internal references to any persistent object; these references are then used, for
example, to catalog objects.

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


Getting object unique ID
------------------------

PyAMS provides a custom interface, which can be used to get the internal ID of an object in
hexadecimal format:

    >>> from persistent.interfaces import IPersistent
    >>> from pyams_utils.interfaces.intids import IUniqueID
    >>> from pyams_utils.tests import MyTestContent

    >>> content = MyTestContent()
    >>> IUniqueID(content, None) is None
    False
    >>> IUniqueID(content, None).oid is None
    True


The default adapter relies on a registered IIntIds utility, which doesn't exist yet:

    >>> import transaction
    >>> from zope.site import LocalSiteManager
    >>> from zope.site.folder import Folder
    >>> from zope.intid.interfaces import IIntIds
    >>> from zope.intid import IntIds
    >>> from pyams_utils.zodb import ZODBConnection

    >>> conn = ZODBConnection()
    >>> root = conn.get_connection().root()
    >>> app = root['application'] = Folder()
    >>> lsm = LocalSiteManager(app, default_folder=False)
    >>> app.setSiteManager(lsm)
    >>> intids = lsm['Internal IDs'] = IntIds()
    >>> lsm.registerUtility(intids, IIntIds)
    >>> app['content'] = content
    >>> transaction.commit()

We may now simulate a request and activate local components registry:

    >>> from pyramid.events import NewRequest
    >>> from pyams_utils.registry import handle_new_request, handle_site_before_traverse
    >>> from zope.traversing.interfaces import BeforeTraverseEvent

    >>> request = DummyRequest()
    >>> handle_new_request(NewRequest(request))
    >>> handle_site_before_traverse(BeforeTraverseEvent(app, request))

    >>> from pyams_utils.registry import query_utility
    >>> query_utility(IIntIds)
    <zope.intid.IntIds object at 0x... oid 0x... in <ZODB.Connection.Connection object at ...>>

    >>> IUniqueID(content, None).oid is None
    False

A unique ID is purely unpredictable...

A function is also available to convert a unique ID into an object key which can be used
as a key in a folder or BTree as object name:

    >>> from pyams_utils.intids import get_object_uid
    >>> get_object_uid(content) == IUniqueID(content).oid
    True

We can also handle objects removal:

    >>> from zope.lifecycleevent import ObjectRemovedEvent

    >>> del app['content']
    >>> event = ObjectRemovedEvent(content, app, 'content')
    >>> config.registry.notify(event)

    >>> query_utility(IIntIds).queryId(content) is None
    True


Tests cleanup:

    >>> from pyams_utils.registry import set_local_registry
    >>> set_local_registry(None)
    >>> tearDown()
