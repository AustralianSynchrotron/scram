# $File: //ASP/proc/wmgmt/scram/trunk/scram/startup.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 13:56:56 $
# Last checked in by: $Author: starritt $
#

import logging
import datetime
import collections
import state_machine
import ordered_enum

import scram

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# These are super-sets of all types of severity and status
#
AlarmSeverityValues = (
    'NO_ALARM', 'MINOR', 'MAJOR', 'INVALID', 'DISCONNECTED', 'UNKNOWN')

AlarmSeverities = ordered_enum.OrderedEnum("AlarmSeverities", AlarmSeverityValues)


AlarmStatusValues = (
    'NO_ALARM',  'READ',   'WRITE',       'HIHI',         'HIGH',         'LOLO',
    'LOW',       'STATE',  'COS',         'COMM',         'TIMEOUT',      'HWLIMIT',
    'CALC',      'SCAN',   'LINK',        'SOFT',         'BAD_SUB',      'UDF',
    'DISABLE',   'SIMM',   'READ_ACCESS', 'WRITE_ACCESS',
    'THRESHOLD', 'DISCONNECTED',  'UNKNOWN')

AlarmStatus = ordered_enum.OrderedEnum("AlarmStatus", AlarmStatusValues)


class AlarmState (collections.namedtuple("AlarmState", ('severity', 'status'))):

    """ Named tuple with nicer str format
    """

    def __str__(self):
        return "AlarmState(sevr=%s,stat=%s)" % (self.severity.name, self.status.name)


# Useful common alarm states
#
no_alarm_state = AlarmState(AlarmSeverities.NO_ALARM, AlarmStatus.NO_ALARM)
unknown_alarm_state = AlarmState(AlarmSeverities.UNKNOWN,  AlarmStatus.UNKNOWN)
disconnected_state = AlarmState(AlarmSeverities.DISCONNECTED, AlarmStatus.DISCONNECTED)


# -----------------------------------------------------------------------------
#
class BaseAlarm:

    """ Base class for any/all alarm types
    """
    _alarm_list = []

    def __init__(self, name, kind="base"):
        self._name = name
        self._kind = kind
        self._alarm_state = unknown_alarm_state
        self._skip_latch_allowed = False
        self._deshelve_duration = 3600.0   # i.e. 1 hour
        self._deshelve_datetime = None

        self._state_machine = state_machine.StateMachine(first_state=NoAlarm,
                                                         context=self,
                                                         name="%-3s:%s" % (self.kind, self.name))
        self._state_machine.enter_first_state ()


        # The state machine time event.
        #
        scram.scanner.register(self._time_event, 5.0)

        # Lastly keep a trach of all alarms.
        #
        BaseAlarm._alarm_list.append(self)

    def __str__(self):
        return "(%s, %s, %s, %s)" % (self.kind, self.name, self.alarm_state, self.mc_state)

    @property
    def name(self):
        return self._name

    @property
    def kind(self):
        return self._kind

    @property
    def severity(self):
        return self._alarm_state.severity

    @property
    def status(self):
        return self._alarm_state.status

    @property
    def alarm_state(self):
        return self._alarm_state

    @property
    def skip_latch_allowed(self):
        return self._skip_latch_allowed

    @skip_latch_allowed.setter
    def skip_latch_allowed(self, value):
        self._skip_latch_allowed = bool(value)

    @property
    def deshelve_duration(self):
        return self._deshelve_duration

    @deshelve_duration.setter
    def deshelve_duration(self, value):
        self._deshelve_duration = float(value)
        # Limit to a max of one day.
        if self._deshelve_duration >= 86400.0:
            self._deshelve_duration = 86400.0

    @property
    def deshelve_datetime(self):
        return self._deshelve_datetime

    @deshelve_datetime.setter
    def deshelve_datetime(self, value):
        self._deshelve_datetime = value

    @property
    def alarm_is_masked(self):
        """ Returns true if alarm hidden, return false if alarm allowed """
        return self.get_alarm_masked_state()

    @property
    def mc_state(self):
        if self._state_machine is None:
            return "under construction"
        return self._state_machine.state_name

    def set_alarm_state(self, new_state):
        # TODO:  Make this method thread safe.

        if self._alarm_state == new_state:
            # No change
            return

        old_state = self.alarm_state    # save old state
        self._alarm_state = new_state   # and the update


        was_in_alarm = (old_state != unknown_alarm_state) and (old_state.severity != AlarmSeverities.NO_ALARM)
        is_in_alarm = (self.severity != AlarmSeverities.NO_ALARM)

        if is_in_alarm != was_in_alarm:
            if is_in_alarm:
                self._alarm_condition_declared()
            else:
                self._alarm_condition_cleared()
        else:
            if is_in_alarm:
                self._alarm_condition_updated()
            else:
                # both no alarm - just status change - strange - log and ignore.
                logger.warn("%s: unexpected alarm state update from %s to %s" %
                           (self.name, old_state, self.alarm_state))

    # Concerete classes should override this function.
    # The function should return true if alarm hidden, return false if alarm allowed
    #
    def get_alarm_masked_state(self):
        raise NotImplementedError(self.__class__.__name__ + ".get_alarm_masked_state()")

    # Functions to create events and pass events to the state machine.
    #
    # Field equipment triggered events...
    #
    def _alarm_condition_declared(self):
        logger.debug("alarm_condition_declared")
        self._state_machine.process_event(Alarm_Condition_Declared())

    def _alarm_condition_updated(self):
        logger.debug("alarm_condition_updated")
        self._state_machine.process_event(Alarm_Condition_Updated())

    def _alarm_condition_cleared(self):
        logger.debug("alarm_condition_cleared")
        self._state_machine.process_event(Alarm_Condition_Cleared())

    # Operator action triggered events...
    #
    def alarm_acknowledged_event(self):
        self._state_machine.process_event(Alarm_Acknowledged())

    def alarm_shelved_event(self):
        self._state_machine.process_event(Alarm_Shelved())

    # System triggered events...
    #
    def _time_event(self):
        self._state_machine.process_event(Time_Event())

    def input_filter_event(self):
        self._state_machine.process_event(Input_Filter_Event())


# -----------------------------------------------------------------------------
# Defines events that may impact the alarm state.
#
class Alarm_Condition_Declared (state_machine.BaseEvent):
    pass


class Alarm_Condition_Updated (state_machine.BaseEvent):
    pass


class Alarm_Condition_Cleared (state_machine.BaseEvent):
    pass


class Alarm_Acknowledged (state_machine.BaseEvent):
    pass


class Alarm_Shelved (state_machine.BaseEvent):
    pass


class Time_Event (state_machine.BaseEvent):

    def __init__(self):
        state_machine.BaseEvent.__init__(self, no_logging=True)


class Input_Filter_Event (state_machine.BaseEvent):
    pass


# -----------------------------------------------------------------------------
# Defines the states and transition rules. State classes themselves hold no
# state information other than the implicitly the current state. The context
# parameter is the the associated alarm instance class object.
#
# The states are:
#   NoAlarm  - first/default case
#   InAlarm  -
#   Latched  -
#   Shelved  -
#   Acknowledged -
#   Masked   -
#
class NoAlarm (state_machine.BaseState):

    @classmethod
    def process_event(cls, context, event):
        alarm = context
        next_state = None

        if isinstance(event, Alarm_Condition_Declared):
            if alarm.alarm_is_masked:
                next_state = Masked
            else:
                next_state = InAlarm

        return next_state


class InAlarm (state_machine.BaseState):

    @classmethod
    def process_event(cls, context, event):
        alarm = context
        next_state = None

        if isinstance(event, Alarm_Condition_Cleared):
            if alarm.skip_latch_allowed:
                next_state = NoAlarm
            else:
                next_state = Latched

        elif isinstance(event, Alarm_Shelved):
            delta = datetime.timedelta(seconds=alarm.deshelve_duration)
            when = datetime.datetime.now() + delta
            alarm.deshelve_datetime = when
            next_state = Shelved

        elif isinstance(event, Alarm_Acknowledged):
            next_state = Acknowledged

        elif isinstance(event, Input_Filter_Event):
            if alarm.alarm_is_masked:
                next_state = Masked

        return next_state


class Latched (state_machine.BaseState):

    @classmethod
    def process_event(cls, context, event):
        alarm = context
        next_state = None

        if isinstance(event, Alarm_Condition_Declared):
            next_state = InAlarm

        elif isinstance(event, Alarm_Acknowledged):
            next_state = NoAlarm

        elif isinstance(event, Input_Filter_Event):
            if alarm.alarm_is_masked:
                next_state = Masked

        return next_state


class Shelved (state_machine.BaseState):

    @classmethod
    def process_event(cls, context, event):
        alarm = context
        next_state = None

        if isinstance(event, Alarm_Condition_Cleared):
            # Once shelved, an alarm cannot go straight to NoAlarm
            next_state = Latched

        elif isinstance(event, Alarm_Acknowledged):
            next_state = Acknowledged

        elif isinstance(event, Time_Event):
            if datetime.datetime.now() >= alarm.deshelve_datetime:
                next_state = InAlarm

        elif isinstance(event, Input_Filter_Event):
            if alarm.alarm_is_masked:
                next_state = Masked

        return next_state


class Acknowledged (state_machine.BaseState):

    @classmethod
    def process_event(cls, context, event):
        alarm = context
        next_state = None

        if isinstance(event, Alarm_Condition_Cleared):
            next_state = NoAlarm

        elif isinstance(event, Input_Filter_Event):
            if alarm.alarm_is_masked:
                next_state = Masked

        return next_state


class Masked (state_machine.BaseState):

    """ Because of system state (e.g. Maintenance), or item out of service,
        or is deemed a consequenctial alarm, an alarm can become masked.
    """
    @classmethod
    def process_event(cls, context, event):
        alarm = context
        next_state = None

        if isinstance(event, Alarm_Condition_Cleared):
            next_state = NoAlarm

        elif isinstance(event, Input_Filter_Event):
            if not alarm.alarm_is_masked:
                next_state = InAlarm

        return next_state

# end
