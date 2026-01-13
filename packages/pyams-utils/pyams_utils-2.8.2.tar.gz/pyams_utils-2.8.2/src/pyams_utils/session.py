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

"""PyAMS_utils session module

This helper module is used to add a "session_property" method decorator, which can be used to
store method result into user's session.

It also adds to function to get and set session data.
"""

from pyams_utils.request import check_request

__docformat__ = 'restructuredtext'


def get_session_data(request, app, key, default=None):
    """Get data associated with current user session

    PyAMS session management is based on :py:mod:`Beaker` package session management.

    :param request: the request from which session is extracted
    :param str app: application name
    :param str key: session data key for given application
    :param default: object; requested session data, or *default* if it can't be found

    .. code-block:: python

        APPLICATION_KEY = 'MyApp'
        SESSION_KEY = 'MyFunction'

        def my_function(request):
            return get_session_data(request, APPLICATION_KEY, SESSION_KEY)
    """
    session = request.session
    return session.get(f'{app}::{key}', default)


def set_session_data(request, app, key, value):
    """Associate data with current user session

    :param request: the request from which session is extracted
    :param str app: application name
    :param str key: session data key for given application
    :param object value: any object that can be pickled can be stored into user session

    .. code-block:: python

        APPLICATION_KEY = 'MyApp'
        SESSION_KEY = 'MyFunction'

        def my_function(request):
            value = {'key1': 'value1', 'key2': 'value2'}
            set_session_data(request, APPLICATION_KEY, SESSION_KEY, value)
    """
    session = request.session
    session[f'{app}::{key}'] = value


_MARKER = object()


def session_property(app, key=None, prefix=None):
    """Define a method decorator used to store result into request's session

    If no request is currently running, a new one is created.

    :param str app: application identifier used to prefix session keys
    :param str key: session's value key; if *None*, the key will be the method's object; if *key*
        is a callable object, il will be called to get the actual session key
    :param prefix: str; prefix to use for session key; if *None*, the prefix will be the property
        name
    """

    def session_decorator(func):

        def wrapper(obj, app, key, *args, **kwargs):
            request = check_request()
            if callable(key):
                key = key(obj, *args, **kwargs)
            if not key:
                key = f'{prefix or func.__name__}::{obj!r}'
            data = get_session_data(request, app, key, _MARKER)
            if data is _MARKER:
                data = func
                if callable(data):
                    data = data(obj, *args, **kwargs)
                set_session_data(request, app, key, data)
            return data

        return lambda x, *args, **kwargs: wrapper(x, app, key, *args, **kwargs)

    return session_decorator
