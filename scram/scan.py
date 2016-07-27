# $File: //ASP/proc/wmgmt/scram/trunk/scram/startup.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 13:56:56 $
# Last checked in by: $Author: starritt $
#

import logging
import datetime
import threading
import time
import heapq

import epics.ca
import interupts

logger = logging.getLogger(__name__)

class Scan (epics.ca.CAThread):

    """
        Note: We did consider sched.scheduler, but rejected because:
              a) want the internal thread to inherit from CA Thread
              b) sched.scheduler only does one off events; and
              c) want to monitor interupts.shutdown_requested in order to determine when to stop.
        However: TODO - see how sched.scheduler uses heapq
    """

    class _Item (object):
        """ Internal scan item
        """
        def __init__(self, method, argument, next_time, period, one_off):
            self._method = method
            self._argument = argument
            self._next_time = next_time
            self._time_delta = datetime.timedelta(seconds=period)
            self._one_off = one_off


    def __init__(self):
        # The set of methods to be called store in a dictionary.
        #
        self._registered_set = {}

        # NOTE: we pass self._run_scan as target.
        #
        epics.ca.CAThread.__init__(self, name="scanning",
                                   target=self._run_scan)
        self.start()


    def register(self, method, period, argument=(), intial_delay=None, one_off=False):
        """  method may an unbounded function, or may be bounded to a class instance object
                 A specific method may only be registered once (it is used as dictionary key
                 If a method needs to be called in more than one circumstance, use a wrapper/partial
             period expressed in seconds - must be convertable to float.
             argument - optional argumet to method
             intial_delay expressed in seconds - if not specified then uses period as intial_delay
             if one_off specified True, then method automatially deregistered BEFORE being called once only.
                 So a one off method cannot re-register itself as it is registered when executed.
        """

        assert hasattr(method, "__call__"), "Scan: method parameter is not callable"

        if method in self._registered_set:
            logger.warn("item already registered: %s", method)
            # but update period??
        else:
            period=float(period)
            if intial_delay is None:
                intial_delay=period
            else:
                intial_delay=float(intial_delay)

            one_off=bool(one_off)

            delta=datetime.timedelta(seconds = intial_delay)
            next_time=datetime.datetime.now() + delta

            scan_item = Scan._Item (method, argument, next_time, period, one_off)
            self._registered_set[method] = scan_item


    def deregister(self, method):
        if method in self._registered_set:
            del self._registered_set[method]
        else:
            logger.warn("item not registered: %s", method)


    def is_registered(self, method):
        return method in self._registered_set


    def _run_scan(self):
        """ _scan_thread target function
        """
        logger.info("scan thread starting")

        while not interupts.shutdown_requested():
            time.sleep(0.5)
            try:
                self._call()
            except Exception:
                # This is unexpected
                logger.error("Exception", exc_info = True)
                time.sleep(0.01)

        logger.info("scan thread complete")


    def _call(self):
        # copy dictionary, but not contents
        # This means that called methods may manipulate the original _registered_set
        #
        baseline = self._registered_set.copy ()
        for method, scan_item in baseline.items():
            try:
                if datetime.datetime.now() >= scan_item._next_time:
                    if scan_item._one_off:
                        self.deregister(method)

                    argument = scan_item._argument
                    method(*argument)

                    if not scan_item._one_off:
                        next_time=datetime.datetime.now() + scan_item._time_delta
                        scan_item._next_time = next_time

            except Exception:
                logger.error("Exception", exc_info = True)


# end
