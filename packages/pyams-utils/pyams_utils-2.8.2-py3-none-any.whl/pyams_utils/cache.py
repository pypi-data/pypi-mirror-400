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

"""PyAMS_utils.cache module

This module provides a small set of adapters which can be used to provide a "cache key" value
to any kind of object.

The goal of such a cache key value is to provide a string representation, as stable as possible,
of a given object; this string can be used as a cache key, but also to define an object ID inside
an HTML page.
A TALES helper extension is also provided to get an object's cache key from a Chameleon template.
"""

from threading import local

from beaker.cache import CacheManager, cache_regions
from persistent.interfaces import IPersistent
from zope.interface import Interface
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces import ICacheKeyValue
from pyams_utils.interfaces.tales import ITALESExtension


__docformat__ = 'restructuredtext'


_CACHES = local()


BEAKER_CACHES_VOCABULARY = SimpleVocabulary([
    SimpleTerm(key, title=f"{key} ({val.get('expire')} sec.)")
    for key, val in sorted(cache_regions.items(),
                           key=lambda x: x[1].get('expire'))
])


def get_cache(name, region, namespace):
    """Get Beaker cache matching region and namespace"""
    try:
        cache = getattr(_CACHES, name)
    except AttributeError:
        manager = CacheManager(**cache_regions[region])
        cache = manager.get_cache(namespace)
        setattr(_CACHES, name, cache)
    return cache


def clear_cache(name, region, namespace):
    """Invalidate cache namespace entries"""
    cache = get_cache(name, region, namespace)
    cache.clear()


@adapter_config(required=object, provides=ICacheKeyValue)
def object_cache_key_adapter(obj):
    """Cache key adapter for any object

    >>> from pyramid.testing import setUp, tearDown
    >>> config = setUp()

    >>> from pyams_utils.interfaces import ICacheKeyValue
    >>> from pyams_utils.cache import object_cache_key_adapter
    >>> config.registry.registerAdapter(object_cache_key_adapter, (object, ), ICacheKeyValue)

    >>> value = object()
    >>> key = ICacheKeyValue(value)
    >>> key == hex(id(value))[2:]
    True

    >>> tearDown()
    """
    return hex(id(obj))[2:]


@adapter_config(required=str, provides=ICacheKeyValue)
def string_cache_key_adapter(obj):
    """Cache key adapter for string value

    >>> from pyramid.testing import setUp, tearDown
    >>> config = setUp()

    >>> from pyams_utils.interfaces import ICacheKeyValue
    >>> from pyams_utils.cache import string_cache_key_adapter
    >>> config.registry.registerAdapter(string_cache_key_adapter, (str, ), ICacheKeyValue)

    >>> value = 'my test string'
    >>> key = ICacheKeyValue(value)
    >>> key == value
    True

    >>> tearDown()
    """
    return obj


@adapter_config(required=IPersistent, provides=ICacheKeyValue)
def persistent_cache_key_adapter(obj):
    """Cache key adapter for persistent object"""
    # pylint: disable=protected-access
    if obj._p_oid:
        return hex(int.from_bytes(obj._p_oid, byteorder='big'))[2:]
    return hex(id(obj))[2:]


@adapter_config(name='cache_key', required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class CacheKeyTalesExtension(ContextRequestViewAdapter):
    """extension:cache_key(context) TALES extension

    A PyAMS TALES extension which allows to render cache key value for a given context.
    """

    def render(self, context=None):
        """Rendering of TALES extension"""
        if context is None:
            context = self.request.context
        return ICacheKeyValue(context)
