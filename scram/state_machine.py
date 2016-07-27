# $File: //ASP/proc/wmgmt/scram/trunk/scram/startup.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 13:56:56 $
# Last checked in by: $Author: starritt $
#

import logging

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# All events inherit from the event base class
# Events may have value.
# Events may also specifiy no logging, in order to inhibit logger.info calls
# This is specifically useful for time events
#
class BaseEvent (object):

    def __init__(self, value=None, no_logging=False):
        self._value = value
        self._no_logging = no_logging

    def __str__(self):
        if self.value is not None:
            image = "%s(%s)" % (self.__class__.__name__, self.value)
        else:
            image = self.__class__.__name__

        return image

    @property
    def value(self):
        return self._value

    @property
    def no_logging(self):
        return self._no_logging


# -----------------------------------------------------------------------------
# Each state of a state machine is represented by a class (and class instance objects)
# Each class type is used as a quazi enumeration type.
#
class BaseState (object):

    def __str__(self):
        return self.__class__.__name__

    # Define the state transition rule.
    # The returned value is either the next state, or None
    # Concrete derived classes MUST implement this function.
    #
    @classmethod
    def process_event(cls, context, event):
        raise NotImplementedError(cls.__name__ + ".process_event()  [classmethod]")

    # Concrete derived classes MAY implement this function.
    # Invoked on entry to state
    #
    @classmethod
    def entry (cls, context):
        pass # print cls.__name__ + ".entry()", str(context)

    # Concrete derived classes MAY implement this function.
    # Invoked on exit from state
    #
    @classmethod
    def exit (cls, context):
        pass # print cls.__name__ + ".exit()", str(context)


# -----------------------------------------------------------------------------
# The state machine engine
#
class StateMachine (object):

    def __init__(self, first_state, name="state_machine", context=None):

        assert issubclass( first_state, BaseState), \
            "state parameter (type %s )is not a state class" % first_state

        self._name = name
        self._context = context   # Anything
        self._state = first_state

    def enter_first_state(self):
        """ This can be problematical if called from __init__
            If first state requires state entry coded to be invoked, this must
            be done explicitly post StateMachine construction.
        """
        self._state.entry (context=self._context)

    def __str__(self):
        return "%s (%s)" % (self.name, self.state_name)

    @property
    def name(self):
        return self._name

    @property
    def state_name(self):
        return self._state.__name__

    def process_event(self, event):
        assert isinstance(event, BaseEvent), \
            "event parameter (type %s) is not an event class" % type(event)

        if not event.no_logging:
            logger.debug("Processing event: %s" % event)

        next_state = self._state.process_event(context=self._context, event=event)
        transition_is_allowed = next_state is not None
        if transition_is_allowed:
            assert issubclass( next_state, BaseState), \
                "next state (type %s )is not a state class" % next_state

            where_we_were = self.state_name

            # exit old state, enter new (possibly the same) state.
            #
            self._state.exit (context=self._context)
            self._state = next_state
            self._state.entry (context=self._context)

            where_we_are = self.state_name

            logger.info("%s transitioned from '%s' to '%s' due to '%s' event" %
                        (self.name, where_we_were, where_we_are, event))
        else:
            if not event.no_logging:
                logger.debug("%s ignored '%s' event" % (self, event))

        return transition_is_allowed

# end
