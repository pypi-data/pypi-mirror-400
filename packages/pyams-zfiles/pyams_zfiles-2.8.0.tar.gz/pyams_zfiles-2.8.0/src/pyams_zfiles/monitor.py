# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from pyams_utils.factory import create_object
from pyams_utils.interfaces.monitor import IMonitorExtension, IMonitorExtensionStatus
from pyams_utils.registry import query_utility, utility_config
from pyams_zfiles.interfaces import IDocumentContainer

__docformat__ = 'restructuredtext'


@utility_config(name='pyams_zfiles.monitor',
                provides=IMonitorExtension)
class ZFilesMonitor:
    """ZFiles monitor utility"""
    
    def get_status(self, request):
        container = query_utility(IDocumentContainer)
        if container is None:
            yield create_object(IMonitorExtensionStatus,
                                handler='pyams_zfiles.monitor:container',
                                status='DOWN',
                                message='Missing document container')
        else:
            yield create_object(IMonitorExtensionStatus,
                                handler='pyams_zfiles.monitor:container',
                                status='UP')
