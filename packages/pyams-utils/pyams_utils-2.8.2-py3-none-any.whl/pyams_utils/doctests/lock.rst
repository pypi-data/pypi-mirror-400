
=======================
PyAMS_utils lock module
=======================

This module is used to handle "global" locks, which are shared between all nodes of an
application cluster (if they share the same cache manager, by using Redis for example).

We first have to initialize a cache:

    >>> from beaker.cache import CacheManager, cache_regions
    >>> cache = CacheManager(**{'cache.type': 'memory'})
    >>> cache_regions.update({'persistent': {'type': 'memory', 'expire': 999999}})

Locks are handled using a "locked" decorator:

    >>> from pyams_utils.lock import CacheLock, locked

    >>> @locked(name='MyLock', wait=False)
    ... def get_locked_value():
    ...     return 1

    >>> value = get_locked_value()
    >>> value
    1

Let's try to start a thread to verify locking:

    >>> with CacheLock(name='MyLock', wait=False):
    ...     value = get_locked_value()
    Traceback (most recent call last):
    ...
    pyams_utils.lock.LockException
