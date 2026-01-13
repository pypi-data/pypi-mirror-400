#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.location module

This module provides a copy hook (copied from zope.location package itself)
to handle copy of located objects.
"""

__docformat__ = 'restructuredtext'

from zope.copy.interfaces import ICopyHook, ResumeCopy
from zope.location import ILocation, inside

from pyams_utils.adapter import ContextAdapter, adapter_config


@adapter_config(required=ILocation,
                provides=ICopyHook)
class LocationCopyHook(ContextAdapter):
    """Location copy hook"""

    def __call__(self, toplevel, register):
        if not inside(self.context, toplevel):
            return self.context
        raise ResumeCopy
