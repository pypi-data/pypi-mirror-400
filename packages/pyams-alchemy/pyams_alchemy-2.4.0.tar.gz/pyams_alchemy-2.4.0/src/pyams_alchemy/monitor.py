# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from sqlalchemy.exc import SQLAlchemyError

from pyams_alchemy.interfaces import IAlchemyEngineUtility
from pyams_utils.factory import create_object
from pyams_utils.interfaces.monitor import IMonitorExtension, IMonitorExtensionStatus
from pyams_utils.registry import get_utilities_for, utility_config

__docformat__ = 'restructuredtext'


@utility_config(name='pyams_alchemy.monitor',
                provides=IMonitorExtension)
class AlchemyMonitor:
    """Alchemy monitor utility"""
    
    def get_status(self, request):
        for name, utility in get_utilities_for(IAlchemyEngineUtility):
            try:
                _engine = utility.get_engine(pool_pre_ping=True)
            except SQLAlchemyError as ex:
                yield create_object(IMonitorExtensionStatus,
                                    handler=f'pyams_alchemy.monitor:{name}',
                                    status='DOWN',
                                    message=f"Can't connect to database: {ex}")
            else:
                yield create_object(IMonitorExtensionStatus,
                                    handler=f'pyams_alchemy.monitor:{name}',
                                    status='UP')
