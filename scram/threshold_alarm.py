# $File: //ASP/proc/wmgmt/scram/trunk/scram/startup.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 13:56:56 $
# Last checked in by: $Author: starritt $
#

import logging
import ordered_enum
import base_alarm
import ca_alarm

from base_alarm import AlarmSeverities
from base_alarm import AlarmStatus
from base_alarm import AlarmState

logger = logging.getLogger(__name__)


class ThresholdAlarm (ca_alarm.ChannelAccessAlarm):

    """ basic threshold check.  Example alarm if/when current falls below 150 mA
        ThresholdAlarm ("Low Current", "CURRENT", "<", "150.0", AlarmState (MAJOR, THRESHOLD))

        dead_band serves both and an input value hysterises dead band, somewhat akin to
        the MDEL filed on many record types

        limit2 - second threshold when the operation is 'in' or 'out'.

        tolerance is the equality tolerance for equality/non-equality tests.

    """

    _allowed_operations = ('==', '!=', '<', '>', '<=', '>=', 'in', 'out')
    _default_state = AlarmState(AlarmSeverities.MINOR, AlarmStatus.THRESHOLD)

    def __init__(self, name, pvname, operation, limit, dead_band,
                 limit2=None, equality_tolerance=None, alarm_state=_default_state):

        ca_alarm.ChannelAccessAlarm.__init__(self, name=name, kind="THR")
        self.skip_latch_allowed = True

        self._operation = operation.strip()
        assert self._operation in ThresholdAlarm._allowed_operations, "Undefined opertion %s" % self._operation

        self._limit = limit
        self._dead_band = dead_band
        self._limit2 = limit2
        self._equality_tolerance = equality_tolerance
        self._threshold_alarm_state = alarm_state

        self._value = None
        self._timestamp = None

        # Create the PV itself.
        #
        self.setup_pv(pvname)

    @property
    def operation(self):
        return self._operation

    @property
    def limit(self):
        return self._limit

    @property
    def dead_band(self):
        return self._dead_band

    @property
    def limit2(self):
        return self._limit2

    @property
    def value(self):
        return self._value

    def get_alarm_masked_state(self):
        return False

    def process_connection(self, connection):
        """ Alarm object connection handler"""
        if not connection.is_connected:
            self._value = None
            self.set_alarm_state(AlarmState(AlarmSeverities.DISCONNECTED,
                                            AlarmStatus.DISCONNECTED))

    def process_update(self, update):
        """ Alarm object update handler."""

        # check for significant value change - do we have a previous value?
        #
        if self._value is not None:
            delta = abs(update.value - self._value)
            if delta <= self.dead_band:
                # No change nothing to see here - move along.
                return

        self._value = update.value
        self._timestamp = update.timestamp

        now_in_alarm = False

        if self._operation == '==':
            delta = abs(self._value - self._limit)
            now_in_alarm = (delta <= self._equality_tolerance)

        elif self._operation == '!=':
            delta = abs(self._value - self._limit)
            now_in_alarm = (delta > self._equality_tolerance)

        elif self._operation == '<':
            now_in_alarm = (self._value < self._limit)

        elif self._operation == '<=':
            now_in_alarm = (self._value <= self._limit)

        elif self._operation == '>':
            now_in_alarm = (self._value > self._limit)

        elif self._operation == '>=':
            now_in_alarm = (self._value >= self._limit)

        elif self._operation == 'in':
            now_in_alarm = (self._value >= self._limit) and (self._value <= self._limit2)

        elif self._operation == 'out':
            now_in_alarm = (self._value < self._limit) or (self._value > self._limit2)

        else:
            logger.error("Unexpected operation %s" % self._operation)

        if now_in_alarm:
            self.set_alarm_state(self._threshold_alarm_state)
        else:
            self.set_alarm_state(base_alarm.no_alarm_state)

# end
