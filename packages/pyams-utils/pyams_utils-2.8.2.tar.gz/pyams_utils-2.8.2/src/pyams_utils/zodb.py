#
# Copyright (c) 2008-2015 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.zodb module

This module provides several utilities used to manage ZODB connections and persistent objects
"""

from ZEO import DB
from ZODB.interfaces import IConnection, IDatabase
from ZODB.utils import p64
from persistent import Persistent
from persistent.interfaces import IPersistent
from pyramid.events import subscriber
from pyramid.interfaces import ISettings
from pyramid_zodbconn import db_from_uri, get_uris
from transaction.interfaces import ITransactionManager
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.container.contained import Contained
from zope.interface import implementer
from zope.lifecycleevent.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.schema import getFieldNames
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces import IOptionalUtility, ZEO_CONNECTIONS_VOCABULARY_NAME, \
    ZODB_CONNECTIONS_VOCABULARY_NAME
from pyams_utils.interfaces.zeo import IZEOConnection
from pyams_utils.registry import get_utility, query_utility
from pyams_utils.vocabulary import LocalUtilitiesVocabulary, vocabulary_config


__docformat__ = 'restructuredtext'


@adapter_config(required=IPersistent,
                provides=IConnection)
def persistent_connection(obj):
    """An adapter which gets a ZODB connection from a persistent object

    We are assuming the object has a parent if it has been created in
    this transaction.

    Raises ValueError if it is impossible to get a connection.
    """
    cur = obj
    while not getattr(cur, '_p_jar', None):
        cur = getattr(cur, '__parent__', None)
        if cur is None:
            return None
    return cur._p_jar  # pylint: disable=protected-access


# IPersistent adapters copied from zc.twist package
# also register this for adapting from IConnection
@adapter_config(required=IPersistent,
                provides=ITransactionManager)
def persistent_transaction_manager(obj):
    """Transaction manager adapter for persistent objects"""
    conn = IConnection(obj)  # typically this will be
                             # zope.keyreference.persistent.connectionOfPersistent
    try:
        return conn.transaction_manager
    except AttributeError:
        return conn._txn_mgr  # pylint: disable=protected-access
        # or else we give up; who knows.  transaction_manager is the more
        # recent spelling.


def load_object(oid, persistent=None):
    """Load object from ZODB"""
    connection = None
    if persistent is not None:
        connection = IConnection(persistent, None)
    if connection is None:
        connection = get_connection_from_settings()
    if isinstance(oid, str):
        oid = p64(int(oid, 16))
    return connection.get(oid)


#
# ZEO connection management
#

@implementer(IZEOConnection)
class ZEOConnection:
    """ZEO connection object

    This object can be used to store all settings to be able to open a ZEO connection.
    Note that this class is required only for tasks specifically targeting a ZEO database
    connection (like a ZEO packer scheduler task); for generic ZODB operations, just use a
    :py:class:`ZODBConnection <pyams_utils.zodb.ZODBConnection>` class defined through Pyramid's
    configuration file.

    Note that a ZEO connection object is a context manager, so you can use it like this:

    .. code-block:: python

        from pyams_utils.zodb import ZEOConnection

        def my_method(zeo_settings):
            zeo_connection = ZEOConnection()
            zeo_connection.update(zeo_settings)
            with zeo_connection as root:
                # *root* is then the ZODB root object
                # do whatever you want with ZEO connection,
                # which is closed automatically
    """

    _storage = None
    _db = None
    _connection = None

    name = FieldProperty(IZEOConnection['name'])
    server_name = FieldProperty(IZEOConnection['server_name'])
    server_port = FieldProperty(IZEOConnection['server_port'])
    storage = FieldProperty(IZEOConnection['storage'])
    username = FieldProperty(IZEOConnection['username'])
    password = FieldProperty(IZEOConnection['password'])
    server_realm = FieldProperty(IZEOConnection['server_realm'])
    blob_dir = FieldProperty(IZEOConnection['blob_dir'])
    shared_blob_dir = FieldProperty(IZEOConnection['shared_blob_dir'])

    def get_settings(self):
        """Get mapping of all connection settings

        These settings can be converted to JSON and sent to another process, for example
        via a ØMQ connection.

        :return: dict
        """
        result = {}
        for name in getFieldNames(IZEOConnection):
            result[name] = getattr(self, name)
        return result

    def update(self, settings):
        """Update connection properties with settings as *dict*

        :param dict settings: typically extracted via the :py:meth:`get_settings` method from
            another process
        """
        names = getFieldNames(IZEOConnection)
        for key, value in settings.items():
            if key in names:
                setattr(self, key, value)

    def get_connection(self, wait_timeout=30, get_storage=False):
        """Create ZEO client connection from current settings

        :param int wait_timeout: connection timeout, in seconds
        :param boolean get_storage: if *True*, the method should return a tuple containing
            storage and DB objects; otherwise only DB object is returned
        :return: tuple containing ZEO client storage and DB object (if *get_storage* argument is
            set to *True*), or only DB object otherwise
        """
        zdb = DB((self.server_name, self.server_port),
                 storage=self.storage,
                 username=self.username or '',
                 password=self.password or '',
                 realm=self.server_realm,
                 blob_dir=self.blob_dir,
                 shared_blob_dir=self.shared_blob_dir,
                 wait_timeout=wait_timeout)
        return (zdb.storage, zdb) if get_storage else zdb

    @property
    def connection(self):
        """Connection getter"""
        return self._connection

    # Context manager methods
    def __enter__(self):
        self._storage, self._db = self.get_connection(get_storage=True)
        self._connection = self._db.open_then_close_db_when_connection_closes()
        return self._connection.root()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection is not None:
            self._connection.close()
        if self._storage is not None:
            self._storage.close()


@implementer(IOptionalUtility, IAttributeAnnotatable)
class ZEOConnectionUtility(ZEOConnection, Persistent, Contained):
    """Persistent ZEO connection utility"""


@subscriber(IObjectAddedEvent, context_selector=IZEOConnection)
def handle_added_connection(event):
    """Register new ZEO connection when added"""
    manager = event.newParent
    manager.registerUtility(event.object, IZEOConnection, name=event.object.name)


@subscriber(IObjectRemovedEvent, context_selector=IZEOConnection)
def handle_removed_connection(event):
    """Un-register ZEO connection when deleted"""
    manager = event.oldParent
    manager.unregisterUtility(event.object, IZEOConnection, name=event.object.name)


@vocabulary_config(name=ZEO_CONNECTIONS_VOCABULARY_NAME)
class ZEOConnectionVocabulary(LocalUtilitiesVocabulary):
    """ZEO connections vocabulary"""

    interface = IZEOConnection


def get_connection_from_settings(settings=None):
    """Load connection matching registry settings"""
    if settings is None:
        settings = get_utility(ISettings)
    for name, uri in get_uris(settings):
        zdb = db_from_uri(uri, name, {})
        return zdb.open()


class ZODBConnection:
    """ZODB connection wrapper

    Connections are extracted from Pyramid's settings file in *zodbconn.uri* entries.

    Note that a ZODB connection object is a context manager, so you can use it like this:

    .. code-block:: python

        from pyams_utils.zodb import ZODBConnection

        def my_method(zodb_name):
            zodb_connection = ZODBConnection(zodb_name)
            with zodb_connection as root:
                # *root* is then the ZODB root object
                # do whatever you want with ZODB connection,
                # which is closed automatically
    """

    def __init__(self, name='', settings=None):
        self.name = name or ''
        if not settings:
            settings = get_utility(ISettings)
        self.settings = settings

    _connection = None
    _db = None
    _storage = None

    @property
    def connection(self):
        """Connection getter"""
        return self._connection

    @property
    def db(self):  # pylint: disable=invalid-name
        """Database getter"""
        return self._db

    @property
    def storage(self):
        """Storage getter"""
        return self._storage

    def get_connection(self):
        """Load named connection matching registry settings"""
        for name, uri in get_uris(self.settings):
            if name == self.name:
                zdb = db_from_uri(uri, name, {})
                connection = self._connection = zdb.open()
                self._db = connection.db()
                self._storage = self.db.storage
                return connection
        return None

    def close(self):
        """Connection close"""
        self._connection.close()
        self._db.close()
        self._storage.close()

    # Context manager methods
    def __enter__(self):
        connection = self.get_connection()
        return connection.root()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


@vocabulary_config(name=ZODB_CONNECTIONS_VOCABULARY_NAME)
class ZODBConnectionVocabulary(SimpleVocabulary):
    """ZODB connections vocabulary"""

    def __init__(self, context=None):  # pylint: disable=unused-argument
        settings = get_utility(ISettings)
        terms = [
            SimpleTerm(name, title=name)
            for name, uri in get_uris(settings)
        ]
        super().__init__(terms)


VOLATILE_MARKER = object()


class volatile_property:  # pylint: disable=invalid-name
    """Property decorator to define volatile attributes into persistent classes"""

    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__

    def __get__(self, inst, cls):
        if inst is None:
            return self
        attrname = f'_v_{self.__name__}'
        value = getattr(inst, attrname, VOLATILE_MARKER)
        if value is VOLATILE_MARKER:
            value = self.fget(inst)
            setattr(inst, attrname, value)
        return value

    def __set__(self, inst, value):
        if inst is None:
            return
        attrname = f'_v_{self.__name__}'
        setattr(inst, attrname, value)

    def __delete__(self, inst):
        attrname = f'_v_{self.__name__}'
        if hasattr(inst, attrname):
            delattr(inst, attrname)
