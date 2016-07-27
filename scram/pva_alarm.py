# $File: //ASP/proc/wmgmt/scram/trunk/scram/startup.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 13:56:56 $
# Last checked in by: $Author: starritt $
#

import logging
import base_alarm

logger = logging.getLogger(__name__)


class PVAccessAlarm (base_alarm.BaseAlarm):

    def __init__(self, name):
        base_alarm.BaseAlarm.__init__(self, name, kind="PV")
        logger.warn("EPICS 4 PV access alarms not available yet")

    def get_alarm_masked_state(self):
        return True

# end
