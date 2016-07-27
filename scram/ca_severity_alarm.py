# $File: //ASP/proc/wmgmt/scram/trunk/scram/startup.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 13:56:56 $
# Last checked in by: $Author: starritt $
#

import collections
import logging
import time

import base_alarm
import ca_alarm

from base_alarm import AlarmSeverities
from base_alarm import AlarmStatus
from base_alarm import AlarmState

logger = logging.getLogger(__name__)


class CASverityAlarm (ca_alarm.ChannelAccessAlarm):

    """ Basic/traditional alarm based on the severity of nominated PV.
    """

    def __init__(self, pvname):
        # Use PV name as alarm name
        #
        ca_alarm.ChannelAccessAlarm.__init__(self, pvname, kind="CA")

        self._value = None
        self._timestamp = None

        # Create the PV itself.
        #
        self.setup_pv(pvname)

    def get_alarm_masked_state(self):
        return False

    def process_connection(self, connection):
        """ Alarm object connection handler"""
        if not connection.is_connected:
            self._value = None
            self.set_alarm_state(AlarmState(AlarmSeverities.DISCONNECTED,
                                            AlarmStatus.DISCONNECTED))

    def process_update(self, update):
        """ Alarm object update handler"""

        # Convert Epics Severity and Status to Scram  Severity and Status
        #
        sevr = ca_alarm.ChannelAccessAlarm._severity_map.get(
            update.severity, AlarmSeverities.UNKNOWN)
        stat = ca_alarm.ChannelAccessAlarm._status_map.get(
            update.status, AlarmStatus.UNKNOWN)

        self._value = update.value
        self._timestamp = update.timestamp
        self.set_alarm_state(AlarmState(sevr, stat))

# end
