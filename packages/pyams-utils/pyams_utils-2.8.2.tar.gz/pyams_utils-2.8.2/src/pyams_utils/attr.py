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

"""PyAMS_utils.attr module

This module provides an :ref:`ITraversable` adapter which can be used to get access to an object's
attribute from a browser URL.
This adapter is actually used to get access to 'file' attributes in PyAMS_file package.
"""

from pyramid.exceptions import NotFound
from zope.interface import Interface
from zope.traversing.interfaces import ITraversable

from pyams_utils.adapter import ContextAdapter, adapter_config


__docformat__ = 'restructuredtext'


@adapter_config(name='attr', required=Interface, provides=ITraversable)
class AttributeTraverser(ContextAdapter):
    """++attr++ namespace traverser

    This custom traversing adapter can be used to access an object attribute directly from
    an URL by using a path like this::

    /path/to/object/++attr++name

    Where *name* is the name of the requested attribute.
    """

    def traverse(self, name, furtherpath=None):  # pylint: disable=unused-argument
        """Traverse from current context to given attribute"""
        if '.' in name:
            name = name.split('.', 1)[0]
        try:
            return getattr(self.context, name)
        except AttributeError as exc:
            raise NotFound from exc
