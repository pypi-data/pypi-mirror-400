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

"""PyAMS_utils list module

This module is dedicated to lists and iterators management. It provides function to extract
unique values from a list or iterator in their original order, or to iterate over an iterator in
random order; it also provides a "boolean_iter" function (usable as TALES extension) to check if
an iterator returns at least one value, without consuming this iterator (the function returns a
tuple containing a boolean value to specify if iterator is empty or not, and the original
iterator).
"""

from itertools import filterfalse, tee, zip_longest
from random import random, shuffle

from zope.interface import Interface

from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.tales import ITALESExtension


__docformat__ = 'restructuredtext'


def is_not_none(item):
    """Simple filter for not None values

    >>> from pyams_utils.list import is_not_none

    >>> is_not_none(None)
    False
    >>> is_not_none(())
    True
    >>> is_not_none(0)
    True
    >>> is_not_none('')
    True
    """
    return item is not None


def unique(seq, key=None):
    """Extract unique values from list, preserving order

    :param iterator seq: input list
    :param callable key: an identity function which is used to get 'identity' value of each element
        in the list
    :return: list; a new list containing only unique elements of the original list in their initial
        order. Original list is not modified.
    """
    seen = set()
    seen_add = seen.add
    result = []
    if key is None:
        for element in filterfalse(seen.__contains__, seq):
            seen_add(element)
            result.append(element)
    else:
        for element in seq:
            k = key(element)
            if k not in seen:
                seen_add(k)
                result.append(element)
    return result


def unique_iter(iterable, key=None):
    """Iterate over iterator values, yielding only unique values

    :param iterator iterable: input iterator
    :param callable key: an identity function which is used to get 'identity' value of each element
        in the list
    :return: an iterator of unique values
    """
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def unique_iter_max(iterable, key, sort_key=None):
    """Get unique items sorted from an iterator
    
    :param iterator iterable: input iterator
    :params callable key: an identity function which is used to get 'identity' value of each element
        in the list
    :param callable sort_key: a function used to sort elements inside each iterable
    :return: an iterator of unique values containing only the last element of each iterator elements
    """
    seen = {}
    for element in iterable:
        k = key(element)
        if k not in seen:
            seen[k] = set()
        seen[k].add(element)
    yield from (
        sorted(v, key=sort_key)[-1]
        for k, v in seen.items()
    )
    
    
def random_iter(iterable, limit=1):
    """Get items randomly from an iterator
    """
    selected = [None] * limit
    for index, item in enumerate(iterable):
        if index < limit:
            selected[index] = item
        else:
            selected_index = int(random() * (index+1))
            if selected_index < limit:
                selected[selected_index] = item
    shuffle(selected)
    return iter(selected)


def boolean_iter(iterable):
    """Check if an iterable returns at least one value, without consuming it.

    The function returns a tuple containing a boolean flag indicating if the original iterator
    is empty or not, and the original un-consumed iterator.
    """

    def inner_check():
        check, items = tee(iterable)
        try:
            next(check)
        except (StopIteration, RuntimeError):
            yield False
        else:
            yield True
            yield from items

    values = inner_check()
    return next(values), values


@adapter_config(name='boolean_iter',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class BooleanIterCheckerExpression(ContextRequestViewAdapter):
    """TALES expression used to handle iterators

    The expression returns a tuple containing a boolean flag indicating if the original iterator
    is empty or not, and the original un-consumed iterator.
    """

    def render(self, context=None):
        """Render TALES extension; see `ITALESExtension` interface"""
        if context is None:
            context = self.context
        return boolean_iter(context)


def grouped_iter(iterable, length, missing=None):
    """Iterate over a set of items, grouped by length value"""
    args = [iter(iterable)] * length
    return zip_longest(*args, fillvalue=missing)


@adapter_config(name='grouped_iter',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class GroupedIterCheckerExpression(ContextRequestViewAdapter):
    """TALES expression used to handle iterators

    The expression returns a list of tuples containing the items of the original iterator,
    grouped by subgroups of given length value.
    """

    def render(self, context=None, length=3, missing=None):
        """Render TALES extension; see `ITALESExtension` interface"""
        if context is None:
            context = self.context
        return grouped_iter(context, length, missing)


@adapter_config(name='tee_iter', context=(Interface, Interface, Interface),
                provides=ITALESExtension)
class IterValuesTeeExpression(ContextRequestViewAdapter):
    """TALES expression used to tee iterators"""

    def render(self, context=None):
        if context is None:
            context = self.context
        return tee(context)


def next_from(value):
    """Return the next value from provided sequence"""
    if not value:
        return None
    try:
        return next(iter(value))
    except TypeError:
        return value


def paginate(items, page_size):
    """Iterate over items by pages of given size"""
    for idx in range(0, len(items), page_size):
        yield items[idx:idx+page_size]
