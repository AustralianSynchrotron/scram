# $File: //ASP/proc/wmgmt/scram/trunk/scram/startup.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 13:56:56 $
# Last checked in by: $Author: starritt $
#

import logging
import base_alarm
import ca_alarm

from base_alarm import AlarmSeverities
from base_alarm import AlarmStatus
from base_alarm import AlarmState

logger = logging.getLogger(__name__)


class CalculationAlarm (ca_alarm.ChannelAccessAlarm):

    """
        name          - alarm name

        pv_names      - set of pv names. This may one of a scalar, tuple, list or dict

        calc_function - uses the values for the pv names to determine alarm state
                        the structure of the parameters passed to the calc_function refect
                        the  structure if the pv_name_list.
    """

    def __init__(self, name, pv_names, calc_function):
        ca_alarm.ChannelAccessAlarm.__init__(self, name=name, kind="CALC")

        assert hasattr(calc_function, "__call__"), "calc_function is not callable"

        self._calc_function = calc_function

        self._use_alarm_state = AlarmState(AlarmSeverities.MAJOR, AlarmStatus.CALC)

        self._pv_names = pv_names
        self._values = None

        # Create _values to have same struture as _pv_names
        # Except a tuple is saved as a list as it is mutable.
        #
        if isinstance(self._pv_names, str):
            # scalar
            pv_name = self._pv_names
            self._values = None
            self.setup_pv(pv_name, index=None)

        elif isinstance(self._pv_names, dict):
            self._values = {}
            for key, pv_name in self._pv_names.items():
                self._values[key] = None
                self.setup_pv(pv_name, index=key)

        elif isinstance(self._pv_names, list):
            self._values = []
            for index, pv_name in enumerate(self._pv_names):
                self._values.append(None)
                self.setup_pv(pv_name, index=index)

        elif isinstance(self._pv_names, tuple):
            self._values = []
            for index, pv_name in enumerate(self._pv_names):
                self._values.append(None)
                self.setup_pv(pv_name, index=index)

        else:
            raise RuntimeError("Unexpected pv_names type: %s" % type(self._pv_names))

#        print self._pv_names
#        print self._values

    def get_alarm_masked_state(self):
        return False

    def process_connection(self, connection):
        """ Alarm object connection handler"""
        if not connection.is_connected:
            self._values[index] = None
            self.set_alarm_state(AlarmState(AlarmSeverities.DISCONNECTED,
                                            AlarmStatus.DISCONNECTED))

    def process_update(self, update):
        """ Alarm object update handler."""

        if isinstance(self._pv_names, str):
            self._values = update.value
            result = self._calc_function(self._values)

        elif isinstance(self._pv_names, dict):
            index = update.index
            assert index in self._values, "index key %s not in dict" % index
            self._values[index] = update.value
            result = self._calc_function(**self._values)

        elif isinstance(self._pv_names, list):
            index = int(update.index)
            assert index >= 0 and index < len(
                self._value), "index %d constraint error" % index
            self._values[index] = update.value
            result = self._calc_function(*self._values)

        elif isinstance(self._pv_names, tuple):
            index = int(update.index)
            assert index >= 0 and index < len(
                self._value), "index %d constraint error" % index
            self._values[index] = update.value
            result = self._calc_function(*tuple(self._values))

        else:
            raise RuntimeError("Unexpected pv_names type: %s" % type(self._pv_names))

        if isinstance(result, AlarmState):
            self.set_alarm_state(result)

        elif isinstance(result, bool):
            if result:
                self.set_alarm_state(self._use_alarm_state)
            else:
                self.set_alarm_state(base_alarm.no_alarm_state)

        else:
            logger.error("Unexpected result value (type): %s (%s)" % (result, type(result)))


# end
