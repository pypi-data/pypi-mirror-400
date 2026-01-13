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

"""PyAMS_utils.property module

"""

__docformat__ = 'restructuredtext'


class cached_property:  # pylint: disable=invalid-name
    """A read-only property decorator that is only evaluated once.

    The value is cached on the object itself rather than the function or class; this should prevent
    memory leakage.
    """
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result


class _ClassPropertyDescriptor:
    """Class property descriptor"""

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, owner):
        try:
            return self.fget(obj)
        except AttributeError:
            return self.fget(owner)

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        return self.fset(obj, value)

    def setter(self, func):
        """Class property setter"""
        self.fset = func
        return self


def _create_type(meta, name, attrs):
    type_name = f'{name}Type'
    type_attrs = {}
    for key, value in attrs.items():
        if isinstance(value, _ClassPropertyDescriptor):
            type_attrs[key] = value
    return type(type_name, (meta,), type_attrs)


class ClassPropertyType(type):
    """Class property type"""

    def __new__(meta, name, bases, attrs):  # pylint: disable=bad-mcs-classmethod-argument
        Type = _create_type(meta, name, attrs)
        cls = super().__new__(meta, name, bases, attrs)
        cls.__class__ = Type
        return cls


def classproperty(func):
    """Main class property decorator"""
    return _ClassPropertyDescriptor(func)
