# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from zope.interface import Interface
from zope.schema import Choice, Text, TextLine

__docformat__ = 'restructuredtext'


MONITOR_API_ROUTE = 'pyams_utils.rest.monitor'
'''REST monitor API route'''

MONITOR_API_PATH = '/api/rest/monitor'
'''REST monitor API default path'''


EXTENSION_STATUS = ('UP', 'DOWN', 'UNKNOWN')

MONITOR_STATUS = ('UP', 'DOWN', 'PARTIAL', 'UNKNOWN')


class IMonitorExtensionStatus(Interface):
    """Monitor extension status interface"""

    handler = TextLine(title="Extension name")

    status = Choice(title="Status value",
                    description="Status value to be displayed in monitor",
                    values=EXTENSION_STATUS)

    message = Text(title="Status information",
                   description="Additional information message about status",
                   required=False)

    def to_dict(self):
        """Get status as a dictionary"""


class IMonitorExtension(Interface):
    """Monitor extension utility interface"""
    
    def get_status(self, request):
        """Returns an iterator over the available extensions status list"""
