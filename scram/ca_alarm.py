# $File: //ASP/proc/wmgmt/scram/trunk/scram/startup.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 13:56:56 $
# Last checked in by: $Author: starritt $
#

import collections
import datetime
import logging
import Queue
import threading
import time

import interupts
import epics

import scram
import base_alarm
from base_alarm import AlarmSeverities
from base_alarm import AlarmStatus
from base_alarm import AlarmState

logger = logging.getLogger(__name__)


class ChannelAccessAlarm (base_alarm.BaseAlarm):

    """ Base class of any CA related alarms, e.g. basic severity alarm and thresdhold alarm.
    """

    # These named tuples are formed from call back data and place in a queue for
    # later processing.
    #
    ca_connection_fields = ("alarm_instance", "index", "is_connected")
    CA_Connection = collections.namedtuple("CA_Connection", ca_connection_fields)

    ca_update_fields = (
        "alarm_instance",  "index", "value", "severity", "status", "timestamp")
    CA_Update = collections.namedtuple("CA_Update", ca_update_fields)

    # Single update queue for now, could have low and high priority queues.
    #
    _ca_process_queue = Queue.Queue()

    # Holds refernce to the thread that processes the _ca_process_queue
    #
    _ca_processing_thread = None

    # Map CA Severty and Status to SCRAM  Severity and Status
    #
    _severity_map = {
        epics.NO_ALARM: AlarmSeverities.NO_ALARM,
        epics.MINOR_ALARM: AlarmSeverities.MINOR,
        epics.MAJOR_ALARM: AlarmSeverities.MAJOR,
        epics.INVALID_ALARM: AlarmSeverities.INVALID
    }

    _status_map = {
        0:  AlarmStatus.NO_ALARM,
        1:  AlarmStatus.READ,
        2:  AlarmStatus.WRITE,
        3:  AlarmStatus.HIHI,
        4:  AlarmStatus.HIGH,
        5:  AlarmStatus.LOLO,
        6:  AlarmStatus.LOW,
        7:  AlarmStatus.STATE,
        8:  AlarmStatus.COS,
        9:  AlarmStatus.COMM,
        10: AlarmStatus.TIMEOUT,
        11: AlarmStatus.HWLIMIT,
        12: AlarmStatus.CALC,
        13: AlarmStatus.SCAN,
        14: AlarmStatus.LINK,
        15: AlarmStatus.SOFT,
        16: AlarmStatus.BAD_SUB,
        17: AlarmStatus.UDF,
        18: AlarmStatus.DISABLE,
        19: AlarmStatus.SIMM,
        20: AlarmStatus.READ_ACCESS,
        21: AlarmStatus.WRITE_ACCESS
    }

    def __init__(self, name, kind):
        base_alarm.BaseAlarm.__init__(self, name=name, kind=kind)

        self._pv_dict = {}

        # Create processing thread if needs be
        #
        if ChannelAccessAlarm._ca_processing_thread is None:
            # Does this need to be a CA thread ?? Don't think so
            #
            thread = threading.Thread(name="ca_updates_processin",
                                      target=ChannelAccessAlarm._process_ca_callbacks)

            ChannelAccessAlarm._ca_processing_thread = thread
            thread.start()

    def setup_pv(self, pvname, index=0):

        if index in self._pv_dict:
            logger.error("%s duplicate index %s" % (self, index))
            return

        # Create the PV and set up call back.
        #
        pv = AlarmPV(owner=self, index=index, pv_name=pvname,
                     connection_callback=ChannelAccessAlarm._ca_connection_handler)
        pv.add_callback(callback=ChannelAccessAlarm._ca_update_handler)

        # Add to the dictionary
        #
        self._pv_dict[index] = pv

    def process_connection(self, connection):
        """ Alarm object connection handler.
            Derived classes must provide this function
        """
        raise NotImplementedError(self.__class__.__name__ + ".process_connection()")

    def process_update(self, update):
        """ Alarm object update handler.
            Derived classes must provide this function
        """
        raise NotImplementedError(self.__class__.__name__ + ".process_connection()")


    @staticmethod
    def join ():
        if ChannelAccessAlarm._ca_processing_thread is not None:
            ChannelAccessAlarm._ca_processing_thread.join ()


    @staticmethod
    def _process_ca_callbacks():
        """ ca_updates_processing_thread target function
        """
        logger.info("ca_updates_processing_thread starting")
        while not interupts.shutdown_requested():

            try:
                item = ChannelAccessAlarm._ca_process_queue.get(block=False)
                try:
                    time.sleep(0.01)  # don't hog all the cpu time, even if we can

                    alarm_instance = item.alarm_instance

                    what_we_were = alarm_instance.alarm_state

                    # Convert static method to a regular method.
                    #
                    if isinstance(item, ChannelAccessAlarm.CA_Connection):
                        pv = alarm_instance._pv_dict[item.index]
                        pv.clear_connection_timeout()
                        alarm_instance.process_connection(item)

                    elif isinstance(item, ChannelAccessAlarm.CA_Update):
                        alarm_instance.process_update(item)

                    else:
                        logger.error("Unexpected item in process queue: %s", type(item))

                    # Log alarm state changes.
                    #
                    if alarm_instance.alarm_state != what_we_were:
                        logger.info("alarm state: %s" % alarm_instance)

                except Exception:
                    logger.error("Exception", exc_info=True)
                    time.sleep(0.01)

            except Queue.Empty:
                # This expected when queue empty
                time.sleep(0.5)

            except Exception:
                # This is un expected
                logger.error("Exception", exc_info=True)
                time.sleep(0.01)

        logger.info("ca_updates_processing_thread complete")

    @staticmethod
    def _ca_connection_handler(pv, pvname, conn):
        """ py epics connection callback handler
            Creates a connection tuple and adds it to processing queue
        """

        # AlarmPV own attributes
        #
        alarm_instance = pv.alarm_instance
        index = pv.alarm_index

        # Form connection tuple
        #
        connection = ChannelAccessAlarm.CA_Connection(alarm_instance, index, conn)

        # Put on queue for later processing.
        # DO NOT create separate thread for each update.
        #
        ChannelAccessAlarm._ca_process_queue.put(connection, block=True)

    @staticmethod
    def _ca_update_handler(value, severity, status, timestamp, cb_info, **kwd):
        """ py epics update callback handler
            Creates an update tuple and adds it to processing queue
        """

        # AlarmPV own attributes
        #
        pv = cb_info[1]
        alarm_instance = pv.alarm_instance
        index = pv.alarm_index

        # Form update tuple
        #
        update = ChannelAccessAlarm.CA_Update(
            alarm_instance, index, value, severity, status, timestamp)

        # Put on queue for later processing.
        # DO NOT create separate thread for each update.
        #
        ChannelAccessAlarm._ca_process_queue.put(update, block=True)


class AlarmPV (epics.PV):

    """ Simple extention to epics.PV class.
        Defines alarm_instance and alarm_index attributes which are needed for the connection
        callback handler, which is not as 'rich' as the update handler mechanism. But given
        that we have to implement this for connection callbacks, we use it for update callbacks
        as well. The use of functools.partials was considered to provide this functionality
        but using a class means we can also provide a means to detect connection timeouts.
    """

    def __init__(self, owner, index, pv_name, **kwd):
        self._alarm_instance = owner
        self._alarm_index = index

        epics.PV.__init__(self, pvname=pv_name, **kwd)

        delta = datetime.timedelta(seconds=4.0)
        timeout = datetime.datetime.now() + delta
        self._alarm_connection_timeout = timeout
        scram.scanner.register(self.check_connection, 1.0)

    @property
    def alarm_instance(self):
        return self._alarm_instance

    @property
    def alarm_index(self):
        return self._alarm_index

    @property
    def alarm_connection_timeout(self):
        return self._alarm_connection_timeout

    def clear_connection_timeout(self):
        self._alarm_connection_timeout = None
        scram.scanner.deregister(self.check_connection)

    def check_connection(self):
        """ Check connection state
        """
        if self.alarm_connection_timeout is not None:
            if datetime.datetime.now() >= self.alarm_connection_timeout:
                self.clear_connection_timeout()

                # treat as a disconnect.
                #
                self.alarm_instance.set_alarm_state(AlarmState(AlarmSeverities.DISCONNECTED,
                                                               AlarmStatus.TIMEOUT))

                logger.warn("alarm state: %s  pv index: %s" %
                            (self.alarm_instance, self.alarm_index))


# end
