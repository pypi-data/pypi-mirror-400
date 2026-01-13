#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.transaction module

This module provides a base transaction decorator and data manger to handle
components which are not transaction-aware by nature, like Elasticsearch
or Redis operations.
"""

import logging
from functools import wraps

import transaction
from transaction.interfaces import ISavepointDataManager
from zope.interface import implementer

from pyams_utils.interfaces.transaction import ITransactionClient


__docformat__ = 'restructuredtext'


LOGGER = logging.getLogger('PyAMS (utils)')


COMMITTED_STATUS = 'Committed'


STATUS_ACTIVE = 'active'
STATUS_CHANGED = 'changed'


_CLIENT_STATE = {}


class Savepoint:
    """Base savepoint"""

    def __init__(self, dm):
        self.dm = dm  # pylint: disable=invalid-name
        self.saved = dm.client.uncommitted.copy()

    def rollback(self):
        """Savepoint rollback"""
        self.dm.client.uncommitted = self.saved.copy()


@implementer(ISavepointDataManager)
class DataManager:
    """Base data manager"""

    def __init__(self, client, transaction_manager):
        self.client = client
        self.transaction_manager = transaction_manager
        t = transaction_manager.get()  # pylint: disable=invalid-name
        t.join(self)
        _CLIENT_STATE[id(client)] = STATUS_ACTIVE
        self._reset()

    def _reset(self):
        """Data manager reset"""
        LOGGER.debug('_reset(%s)', self)
        self.client.uncommitted = []

    def _finish(self):
        """Data manager finish"""
        LOGGER.debug('_finish(%s)', self)
        client = id(self.client)
        if client in _CLIENT_STATE:
            del _CLIENT_STATE[client]

    def abort(self, trans):  # pylint: disable=unused-argument
        """Transaction abort"""
        LOGGER.debug(f'abort({self})')
        self._reset()
        self._finish()

    def tpc_begin(self, trans):  # pylint: disable=unused-argument
        """Begin two-phases commit"""
        LOGGER.debug(f'tpc_begin({self})')

    def commit(self, trans):  # pylint: disable=unused-argument
        """Transaction commit"""
        LOGGER.debug(f'commit({self})')

    def tpc_vote(self, trans):  # pylint: disable=unused-argument
        """Two-phases commit vote"""
        LOGGER.debug(f'tpc_vote({self})')
        # XXX: Ideally, we'd try to check the uncommitted queue and make sure
        # everything looked ok. Not sure how we can do that, though.

    def tpc_finish(self, trans):  # pylint: disable=unused-argument
        """Two-phases commit finish"""
        # Actually persist the uncommitted queue.
        LOGGER.debug(f'tpc_finish({self})')
        LOGGER.info(f'running: {self.client.uncommitted!r}')
        for cmd, args, kwargs in self.client.uncommitted:
            kwargs['immediate'] = True
            getattr(self.client, cmd)(*args, **kwargs)
        self._reset()
        self._finish()

    def tpc_abort(self, trans):  # pylint: disable=unused-argument
        """Two-phases commit abort"""
        LOGGER.debug('tpc_abort()')
        self._reset()
        self._finish()

    def sortKey(self):  # pylint: disable=invalid-name
        """Data manager sort key getter"""
        # NOTE: Ideally, we want this to sort *after* database-oriented data
        # managers, like the SQLAlchemy one. The double tilde should get us
        # to the end.
        return f'~~transaction-{str(id(self))}'

    def savepoint(self):
        """Savepoint getter"""
        return Savepoint(self)


def join_transaction(client, transaction_manager):
    """Join current transaction"""
    client_id = id(client)
    existing_state = _CLIENT_STATE.get(client_id, None)
    if existing_state is None:
        LOGGER.info(f'client {client_id} not found, setting up new data manager')
        DataManager(client, transaction_manager)
    else:
        LOGGER.info(f'client {client_id} found, using existing data manager')
        _CLIENT_STATE[client_id] = STATUS_CHANGED


def transactional(f):  # pylint: disable=invalid-name
    """Transactional functions wrapper"""

    @wraps(f)
    def transactional_inner(client, *args, **kwargs):
        """Inner transaction wrapper"""
        immediate = kwargs.pop('immediate', None)
        if client.use_transaction:
            if immediate:
                return f(client, *args, **kwargs)
            LOGGER.debug(f'enqueueing action: {f.__name__}: {args!r}, {kwargs!r}')
            join_transaction(client, client.transaction_manager)
            client.uncommitted.append((f.__name__, args, kwargs))
            return None
        return f(client, *args, **kwargs)

    return transactional_inner


@implementer(ITransactionClient)
class TransactionClient:
    """Base transaction client"""

    def __init__(self,
                 use_transaction=True,
                 transaction_manager=transaction.manager):
        self.use_transaction = use_transaction
        self.transaction_manager = transaction_manager
