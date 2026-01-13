#
# Copyright (c) 2015-2024 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.finder module

This module provides functions which can be used to *find* objects 
which are located inside a container and which match specific conditions.
"""

__docformat__ = 'restructuredtext'

from typing import Callable

from persistent.interfaces import IPersistent
from zope.interface import Interface
from zope.location.interfaces import ISublocations


def find_objects_matching(root: IPersistent,
                          condition: Callable,
                          ignore_root: bool = False,
                          with_depth: bool = False,
                          initial_depth: int = 0):
    """Find all objects in root that match the condition

    The condition is a Python callable object that takes an object as
    argument and must return a boolean result.

    All sub-objects of the root will also be searched recursively.

    :param object root: the parent object from which search is started
    :param callable condition: a callable object which may return true for a given
        object to be selected
    :param boolean ignore_root: if *True*, the root object will not be returned, even if it
        matches the given condition
    :param boolean with_depth: if *True*, iterator elements will be made of tuples made of
        found elements and their respective depth
    :param int initial_depth: initial depth of the root element; this argument is mainly used
        when function is called recursively
    :return: an iterator for all root's sub-objects matching condition
    """
    if (not ignore_root) and condition(root):
        yield (root, initial_depth) if with_depth else root
    locations = ISublocations(root, None)
    if locations is not None:
        for location in locations.sublocations():  # pylint: disable=too-many-function-args
            if condition(location):
                yield (location, initial_depth+1) if with_depth else location
            yield from find_objects_matching(location, condition,
                                             ignore_root=True,
                                             with_depth=with_depth,
                                             initial_depth=initial_depth+1)


def find_objects_providing(root: IPersistent,
                           interface: Interface,
                           ignore_root: bool = False,
                           with_depth: bool = False):
    """Find all objects in root that provide the specified interface

    All sub-objects of the root will also be searched recursively.

    :param object root: object; the parent object from which search is started
    :param Interface interface: interface; an interface that sub-objects should provide
    :param boolean ignore_root: if *True*, the root object will not be returned, even if it
        provides the given interface
    :param boolean with_depth: if *True*, iterator elements will be made of tuples made of
        found elements and their respective depth
    :return: an iterator for all root's sub-objects that provide the given interface
    """
    yield from find_objects_matching(root, interface.providedBy, ignore_root, with_depth)
