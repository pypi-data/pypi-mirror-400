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

"""PyAMS_utils.wsgi module

This module provides a method decorator which can store it's value into request environment
"""

__docformat__ = 'restructuredtext'


def wsgi_environ_cache(*names, store_none=True):
    """Wrap a function/method to cache its result for call into request.environ

    :param [string...] names: keys to cache into environ; len(names) must
        be equal to the result's length or scalar
    :param bool store_none: if False, None values are not stored into request environment
    """

    def decorator(func):

        def function_wrapper(self, request, **kwargs):
            scalar = len(names) == 1
            args_key = ''
            if kwargs:
                args_key += ':' + ':'.join((
                    f'{key}={value}'
                    for key, value in kwargs.items()
                ))
            try:
                env = [
                    request.environ[f'{cached_key}{args_key}']
                    for cached_key in names
                ]
            except KeyError:
                env = func(self, request, **kwargs)
                if scalar:
                    env = [env, ]
                for idx, cached_key in enumerate(names):
                    if store_none or (env[idx] is not None):
                        request.environ[f'{cached_key}{args_key}'] = env[idx]
            return env[0] if scalar else env

        return function_wrapper

    return decorator
