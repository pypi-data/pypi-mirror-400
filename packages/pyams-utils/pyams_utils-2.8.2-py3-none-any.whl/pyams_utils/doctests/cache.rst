
========================
PyAMS_utils cache module
========================

This module is used to provide a few helpers related to cache management ; the ICacheKey
interface is used to get a cache key value for any object:

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

    >>> from pyams_utils.zodb import ZODBConnection
    >>> from pyams_utils.tests import MyTestContent

    >>> import transaction
    >>> conn = ZODBConnection()
    >>> content = MyTestContent()

    >>> from pyams_utils.interfaces import ICacheKeyValue
    >>> ICacheKeyValue(content)
    '...'
    >>> int(ICacheKeyValue(content), 16) > 1
    True

    >>> with conn as root:
    ...     root['content'] = content
    ...     transaction.commit()

    >>> ICacheKeyValue(content)
    '1'

A TALES extension is also available to get a cache key from a Chameleon template:

    >>> request = DummyRequest(context=content)
    >>> from pyams_utils.interfaces.tales import ITALESExtension
    >>> extension = config.registry.getMultiAdapter((content, request, None), ITALESExtension,
    ...                                             name='cache_key')
    >>> extension.render()
    '1'
    >>> extension.render(content)
    '1'


Cache management functions and vocabulary
-----------------------------------------

Let's declare a few caches:

    >>> from beaker.cache import CacheManager, cache_regions
    >>> cache = CacheManager(**{'cache.type': 'memory'})
    >>> cache_regions.update({'short': {'type': 'memory', 'expire': 10}})
    >>> cache_regions.update({'long': {'type': 'memory', 'expire': 600}})

We can now get an easy access to any cache:

    >>> from pyams_utils.cache import get_cache, clear_cache
    >>> my_cache = get_cache('pyams_utils', 'short', 'test::ns')
    >>> my_cache
    <beaker.cache.Cache object at 0x...>
    >>> my_cache.set_value('test_value', 1)
    >>> my_cache.get_value('test_value')
    1

    >>> clear_cache('myams_utils', 'short', 'test::ns')
    >>> my_cache.get_value('test_value')
    Traceback (most recent call last):
    ...
    KeyError: b'test_value'


Tests cleanup:

    >>> tearDown()
