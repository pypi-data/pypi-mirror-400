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

"""PyAMS_utils.decorator module

This module only provides a single decorator, which can be used to mark a function as
deprecated.
"""

import functools
import warnings

__docformat__ = 'restructuredtext'


def deprecated(*msg):
    """This is a decorator which can be used to mark functions as deprecated.

    It will result in a warning being emitted when the function is used.

    >>> from pyams_utils.context import capture_stderr
    >>> from pyams_utils.decorator import deprecated

    >>> @deprecated
    ... def my_function(value):
    ...     return value

    >>> with capture_stderr(my_function, 1) as (result, err):
    ...     print(err.split('\\n')[0])
    <doctest ... DeprecationWarning: Function my_function is deprecated.

    >>> @deprecated('Deprecation message')
    ... def my_function_2(value):
    ...     return value

    >>> with capture_stderr(my_function_2, 2) as (result, err):
    ...     print(err.split('\\n')[0])
    <doctest ... DeprecationWarning: Function my_function_2 is deprecated. Deprecation message
    """

    def decorator(func):
        """Actual decorator"""

        @functools.wraps(func)
        def new_func(*args, **kwargs):
            """Wrapped decorator function"""
            warnings.warn_explicit("Function %s is deprecated. %s" % (func.__name__, message),
                                   category=DeprecationWarning,
                                   filename=func.__code__.co_filename,
                                   lineno=func.__code__.co_firstlineno + 1)
            return func(*args, **kwargs)
        return new_func

    if len(msg) == 1 and callable(msg[0]):
        message = u''
        return decorator(msg[0])
    message = msg[0]
    return decorator
