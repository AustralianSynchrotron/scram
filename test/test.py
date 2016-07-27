#!/usr/bin/env  python
#
# $File: //ASP/proc/wmgmt/scram/trunk/scram/startup.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 13:56:56 $
# Last checked in by: $Author: starritt $
#

import logging
import sys
import time
import epics.ca

import scram.state_machine
import scram.scan
import scram.base_alarm
import scram.ca_alarm
import scram.ca_severity_alarm
import scram.threshold_alarm
import scram.calculation_alarm

import scram.record_fields
import scram.pva_alarm
import scram.startup
import scram.main

from scram import program_name, __version__, interupts

from scram.base_alarm import AlarmSeverities
from scram.base_alarm import AlarmStatus
from scram.base_alarm import AlarmState


#from scram.calc_alarm import Operation

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
def set_logging_paradigm(loglevel):
    """Set up the root logger"""

    root_logger = logging.getLogger()

    # Set up logging
    #
    log_format = "%s%s" % ("%(asctime)s.%(msecs)03d %(levelname)-7s ",
                           "%(lineno)4d %(module)-20s %(message)s")


    formatter = logging.Formatter(fmt=log_format, datefmt="%Y-%m-%d %H:%M:%S")

    trfh = logging.StreamHandler (sys.stdout)
    trfh.setFormatter(formatter)

    root_logger.addHandler(trfh)

    # Convert string to level
    level = logging.getLevelName(loglevel)
    root_logger.setLevel(level)

# -----------------------------------------------------------------------------
sector = 0
def createa ():
    global sector
    sector += 1
    if sector > 40:
        scram.scanner.deregister (createa)
        return
  
    scram.ca_severity_alarm.CASverityAlarm ("SR%02dCCG01:PRESSURE_MONITOR" % sector)
    scram.ca_severity_alarm.CASverityAlarm ("SR%02dCCG02:PRESSURE_MONITOR" % sector)
    scram.ca_severity_alarm.CASverityAlarm ("SR%02dCCG03:PRESSURE_MONITOR" % sector)
    scram.ca_severity_alarm.CASverityAlarm ("SR%02dCCG04:PRESSURE_MONITOR" % sector)
    scram.ca_severity_alarm.CASverityAlarm ("SR%02dCCG05:PRESSURE_MONITOR" % sector)

    scram.ca_severity_alarm.CASverityAlarm ("SR%02dPRG01:PRESSURE_MONITOR" % sector)
    scram.ca_severity_alarm.CASverityAlarm ("SR%02dPRG02:PRESSURE_MONITOR" % sector)
    scram.ca_severity_alarm.CASverityAlarm ("SR%02dPRG03:PRESSURE_MONITOR" % sector)
    scram.ca_severity_alarm.CASverityAlarm ("SR%02dPRG04:PRESSURE_MONITOR" % sector)
    scram.ca_severity_alarm.CASverityAlarm ("SR%02dPRG05:PRESSURE_MONITOR" % sector)



# -----------------------------------------------------------------------------
def createb ():
    scram.ca_severity_alarm.CASverityAlarm ("SR11BCM01:CURRENT_MONITOR")
    scram.threshold_alarm.ThresholdAlarm ("Low Current",
                                          "SR11BCM01:CURRENT_MONITOR",
                                          operation="<",
                                          limit=202.0, dead_band=0.1)


# -----------------------------------------------------------------------------
def createc ():
    def combine (c, l):
        """ Test function for CalculationAlarm
        """
        if c is not None and l is not None:
            return (c*l/1000.0) < 5.2
        return None

    scram.calculation_alarm.CalculationAlarm ("Sum Calc",
                                              {'c' : "SR11BCM01:CURRENT_MONITOR",
                                               'l' : "SR11BCM01:LIFETIME_MONITOR" },
                                              combine)


# -----------------------------------------------------------------------------
def run ():
    set_logging_paradigm (logging.DEBUG)
    print ("%s version %s" % (program_name, __version__))

    epics.ca.initialize_libca() # force epics initialization
    scram.scanner = scram.scan.Scan ()
    interupts.setup()

    scram.scanner.register (method=createa, period=0.66667, intial_delay=3.0)
    scram.scanner.register (method=createb, period=1.0, one_off=True)
    scram.scanner.register (method=createc, period=2.0, one_off=True)

    while not interupts.shutdown_requested():
        time.sleep (1.0)

    scram.scanner.join ()
    scram.ca_alarm.ChannelAccessAlarm.join ()

    print ("%s version complete" % program_name)

if __name__ == "__main__":
    run ()

# end
