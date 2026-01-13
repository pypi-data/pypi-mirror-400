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

"""PyAMS_utils.interfaces.zeo module

This module provides interface definition for a ZEO connection
"""

from zope.interface import Attribute, Interface
from zope.schema import Bool, Int, Password, TextLine


__docformat__ = 'restructuredtext'

from pyams_utils import _


class IZEOConnection(Interface):
    """ZEO connection settings interface"""

    name = TextLine(title=_("Connection name"),
                    description=_("Registration name of ZEO connection"),
                    required=True)

    server_name = TextLine(title=_("ZEO server name"),
                           description=_("Hostname of ZEO server"),
                           required=True,
                           default='localhost')

    server_port = Int(title=_("ZEO server port"),
                      description=_("Port number of ZEO server"),
                      required=True,
                      default=8100)

    storage = TextLine(title=_("ZEO server storage"),
                       description=_("Storage name on ZEO server"),
                       required=True,
                       default='1')

    username = TextLine(title=_("ZEO user name"),
                        description=_("User name on ZEO server; only for ZEO server before 5.0"),
                        required=False)

    password = Password(title=_("ZEO password"),
                        description=_("User password on ZEO server; only for ZEO server "
                                      "before 5.0"),
                        required=False)

    server_realm = TextLine(title=_("ZEO server realm"),
                            description=_(
                                "Realm name on ZEO server; only for ZEO server before 5.0"),
                            required=False)

    blob_dir = TextLine(title=_("BLOBs directory"),
                        description=_("Directory path for blob data"),
                        required=False)

    shared_blob_dir = Bool(title=_("Shared BLOBs directory ?"),
                           description=_(
                               "Flag whether the blob_dir is a server-shared filesystem "
                               "that should be used instead of transferring blob data over zrpc."),
                           required=True,
                           default=False)

    connection = Attribute("Current ZEO connection")

    def get_settings(self):
        """Get ZEO connection setting as a JSON dict"""

    def update(self, settings):
        """Update internal fields with given settings dict"""

    def get_connection(self, wait_timeout=30, get_storage=False):
        """Open ZEO connection with given settings"""
