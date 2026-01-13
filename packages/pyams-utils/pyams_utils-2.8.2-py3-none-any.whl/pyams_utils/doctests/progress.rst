
===========================
PyAMS_utils progress module
===========================

PyAMS_utils "progress" module can be used to check progression of long-running tasks.

This module relies on several components:

 - a shared cache (like Redis), which is used to store tasks progress indicators

 - a running task, which will store it's progress indicators into the cache

 - a progress checker task, which will run in parallel and launch queries into the cache to
   get progress indicators.

We first have to initialize a cache:

    >>> import pprint

    >>> from beaker.cache import CacheManager, cache_regions
    >>> cache = CacheManager(**{'cache.type': 'memory'})
    >>> cache_regions.update({
    ...     'default': {'type': 'memory', 'expire': 999999},
    ...     'persistent': {'type': 'memory', 'expire': 999999}
    ... })

The "default" cache is used to store tasks list; the "persistent" cache is used to store
progress indicators of all tasks.

Please note that all module functions are using a global lock in the persistent cache.

    >>> from pyams_utils.progress import get_running_tasks, init_progress_status, \
    ...     get_progress_status, set_progress_status

    >>> get_running_tasks()
    set()

    >>> import uuid
    >>> task_id = str(uuid.uuid1())
    >>> task_id
    '...-...-...-...-...'

    >>> get_progress_status(task_id)
    {'status': 'unknown'}

    >>> init_progress_status(task_id, 'principal.id', "Test task", length=100, current=0)
    >>> task_id in get_running_tasks()
    True
    >>> pprint.pprint(get_progress_status(task_id))
    {'current': 0,
     'label': 'Test task',
     'length': 100,
     'owner': 'principal.id',
     'started': '...T...',
     'status': 'running',
     'tags': None}

    >>> set_progress_status(task_id, length=100, current=50)
    >>> pprint.pprint(get_progress_status(task_id))
    {'current': 50,
     'label': 'Test task',
     'length': 100,
     'message': None,
     'owner': 'principal.id',
     'started': '...T...',
     'status': 'running',
     'tags': None}

    >>> set_progress_status(task_id, length=100, current=100, status='finished')
    >>> pprint.pprint(get_progress_status(task_id))
    {'current': 100,
     'label': 'Test task',
     'length': 100,
     'message': None,
     'owner': 'principal.id',
     'started': '...T...',
     'status': 'finished',
     'tags': None}

Getting status of a finished task is removing it from tasks list:

    >>> get_progress_status(task_id)
    {'status': 'unknown'}
    >>> task_id in get_running_tasks()
    False


Progress status view
--------------------

    >>> from pyramid.testing import DummyRequest
    >>> from pyams_utils.progress import get_progress_status_view

    >>> request = DummyRequest()
    >>> get_progress_status_view(request)
    Traceback (most recent call last):
    ...
    pyramid.httpexceptions.HTTPBadRequest: Missing argument

    >>> task_id = str(uuid.uuid1())
    >>> request = DummyRequest(params={'progress_id': task_id})
    >>> get_progress_status_view(request)
    {'status': 'unknown'}

    >>> set_progress_status(task_id, length=100, current=50)
    >>> pprint.pprint(get_progress_status_view(request))
    {'current': 50, 'length': 100, 'message': None, 'status': 'running'}
