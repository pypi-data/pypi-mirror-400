#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""
Generic test cases for pyams_utils doctests
"""

__docformat__ = 'restructuredtext'

import os
import sys

from persistent import Persistent
from zope.container.folder import Folder
from zope.interface import Interface, implementer
from zope.location import Location


def get_package_dir(value):
    """Get package directory"""

    package_dir = os.path.split(value)[0]
    if package_dir not in sys.path:
        sys.path.append(package_dir)
    return package_dir


class MyTestContent(Persistent, Location):
    """Persistent class"""


class IMyFolder(Interface):
    """Folder marker interface"""


@implementer(IMyFolder)
class MyFolder(Folder):
    """Test folder class"""

    name = ''

    def __init__(self):
        super().__init__()
        self.value = object()
