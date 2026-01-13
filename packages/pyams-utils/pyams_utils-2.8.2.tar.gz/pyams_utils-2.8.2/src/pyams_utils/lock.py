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

"""PyAMS_utils.lock module

This module is use to manage shared locks; these locks can be used accross several
processes; the lock relies on a shared value stored info Beaker's cache.
"""

import time
from threading import local

from beaker import cache


__docformat__ = 'restructuredtext'


_LOCAL = local()


def get_locks_cache():
    """Get locks shared cache"""
    try:
        locks_cache = _LOCAL.locks_cache
    except AttributeError:
        manager = cache.CacheManager(**cache.cache_regions['persistent'])
        locks_cache = _LOCAL.locks_cache = manager.get_cache('PyAMS::locks')
    return locks_cache


class LockException(Exception):
    """Cache lock exception"""


class CacheLock:
    """Beaker based lock

    This lock can be used when you need to get a lot across several processes or even computers.
    The lock relies on a shared value stored into a shared Beaker cache.

    :param str name: name of the lock to use as shared key
    :param boolean wait: if *False*, a *LockException* is raised if lock can't be taken; otherwise,
        application waits until lock is released

    Lock can be used as a context manager.
    """

    def __init__(self, name, wait=True):
        self.key = f'PyAMS::lock::{name}'
        self.wait = wait
        self.has_lock = False

    def __enter__(self):
        locks_cache = get_locks_cache()
        while True:
            test = locks_cache.has_key(self.key)
            if test:
                if not self.wait:
                    raise LockException()
                time.sleep(0.1)
            else:
                locks_cache.set_value(self.key, 1)
                self.has_lock = True
                return

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.has_lock:
            get_locks_cache().remove_value(self.key)
        return False


def locked(name, wait=True):
    """Locked function decorator

    Can be used with any function or method which requires a global shared lock.

    :param str name: name of the lock to use as shared key
    :param boolean wait: if *False*, a *LockException* is raised if lock can't be taken; otherwise,
        application waits until lock is released
    """

    def lock_decorator(func):

        def wrapper(*args, **kwargs):
            with CacheLock(name, wait):
                return func(*args, **kwargs)

        return wrapper

    return lock_decorator
