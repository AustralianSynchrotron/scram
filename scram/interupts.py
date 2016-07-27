# $File: //ASP/tec/exc/mallard/trunk/mallard/interupts.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 10:27:09 $
# Last checked in by: $Author: starritt $
#
# Description
# This file is part of the Mallard experiment control sequence engine.
#
# Copyright (c) 2016 Australian Synchrotron
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# Licence as published by the Free Software Foundation; either
# version 2.1 of the Licence, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public Licence for more details.
#
# You should have received a copy of the GNU Lesser General Public
# Licence along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Contact details:
# andrew.starritt@synchrotron.org.au
# 800 Blackburn Road, Clayton, Victoria 3168, Australia.
#

import signal
import logging

logger = logging.getLogger(__name__)


def setup():
    """Capture sig int and sig term"""
    signal.signal(signal.SIGTERM, _terminate_signal_handler)
    signal.signal(signal.SIGINT, _terminate_signal_handler)


# -----------------------------------------------------------------------------
#
def shutdown_requested():
    return _shutdown_requested

# -----------------------------------------------------------------------------
#


def request_shutdown(exit_code=0):
    global _shutdown_requested
    global _exit_code

    logger.info("programatical shutdown requested")
    _shutdown_requested = True
    _exit_code = exit_code


# -----------------------------------------------------------------------------
#
def exit_code():
    return _exit_code


# -----------------------------------------------------------------------------
#
def _terminate_signal_handler(sig, frame):
    global _shutdown_requested
    global _exit_code

    if sig == signal.SIGTERM:
        signal_name = "SIGTERM"

    elif sig == signal.SIGINT:
        signal_name = "SIGINT"
    else:
        signal_name = "Signal " + str(sig)

    logger = logging.getLogger(__name__)
    logger.info(signal_name + " received, initiating orderly shutdown")

    _shutdown_requested = True
    _exit_code = 128 + sig


_shutdown_requested = False
_exit_code = 0

# end
