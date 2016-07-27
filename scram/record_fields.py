# $File: //ASP/proc/wmgmt/scram/trunk/scram/startup.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 13:56:56 $
# Last checked in by: $Author: starritt $
#

# record field name functions


class RecordField (object):

    def __init__(self, pv_name):
        self._pv_name = pv_name

    def __repr__ (self):
        return "RecordField(%r)" % self._pv_name

    def __str__ (self):
        return self._pv_name

    @property
    def pv_name(self):
        return self._pv_name

    # Extracts record name from PV name, e.g.:
    #
    # SR11BCM01:CURRENT_MONITOR.PREC => SR11BCM01:CURRENT_MONITOR
    # SR11BCM01:CURRENT_MONITOR.VAL  => SR11BCM01:CURRENT_MONITOR
    # SR11BCM01:CURRENT_MONITOR.     => SR11BCM01:CURRENT_MONITOR
    # SR11BCM01:CURRENT_MONITOR      => SR11BCM01:CURRENT_MONITOR
    #
    @property
    def record_name(self):
        dot_posn = self._pv_name.find(".")
        if dot_posn >= 0:
            result = self._pv_name[0:dot_posn]
        else:
            result = pv_name
        return result


    # Extracts field name from PV name, e.g.:
    #
    # SR11BCM01:CURRENT_MONITOR.PREC => PREC
    # SR11BCM01:CURRENT_MONITOR.VAL  => VAL
    # SR11BCM01:CURRENT_MONITOR.     => VAL (it's the default)
    # SR11BCM01:CURRENT_MONITOR      => VAL (it's the default)
    #
    @property
    def field_name(self):
        result = "VAL"
        dot_posn = self._pv_name.find(".")
        if dot_posn >= 0:
            if len(self._pv_name) - (dot_posn + 1) > 0:
                result = self._pv_name[dot_posn + 1:]

        return result


    # Formm field PV name, e.g.:
    #
    # (SR11BCM01:CURRENT_MONITOR.PREC, EGU) => SR11BCM01:CURRENT_MONITOR.EGU
    # (SR11BCM01:CURRENT_MONITOR,      EGU) => SR11BCM01:CURRENT_MONITOR.EGU
    #
    def field_pv_name(self, field):
        return "%s.%s" % (self.record_name, field)


    # Form pseudo field record type PV name, e.g.:
    #
    # SR11BCM01:CURRENT_MONITOR.PREC => SR11BCM01:CURRENT_MONITOR.RTYP
    #
    @property
    def rtype_pv_name(self):
        return self.field_pv_name("RTYP")

# end
