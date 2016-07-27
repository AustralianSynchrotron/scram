# $File: //ASP/proc/wmgmt/scram/trunk/scram/startup.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 13:56:56 $
# Last checked in by: $Author: starritt $
#

import epics.ca
import interupts
import scan
import ca_alarm

def execute():
    epics.ca.initialize_libca() # force epics initialization prior to creating any threads
    scanner = scan.Scan ()
    interupts.setup()

    # TODO: read config file/database and create alarm objects

    # Run forever until a shut down has been requested.
    #
    while not interupts.shutdown_requested():
        time.sleep (1.0)

    scanner.join ()
    ca_alarm.ChannelAccessAlarm.join ()

# end
