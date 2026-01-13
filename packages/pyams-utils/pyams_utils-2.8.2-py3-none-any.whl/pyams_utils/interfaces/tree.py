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

"""PyAMS_utils.interfaces.tree module

The interfaces provided by this module are used to manage trees.
"""

from zope.interface import Interface, Attribute


class INode(Interface):
    """Tree node interface"""

    context = Attribute("Node's context")

    label = Attribute("Node's label")

    css_class = Attribute("Node's CSS class")

    order = Attribute("Node's order")

    def get_level(self):
        """Get depth level of current node"""

    def has_children(self, filter_value=None):
        """Check if current node has children"""

    def get_children(self, filter_value=None):
        """Get list of node children"""


class ITree(Interface):
    """Tree interface"""

    def get_root_nodes(self):
        """Get list of root nodes"""
