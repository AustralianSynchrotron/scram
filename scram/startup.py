# $File: //ASP/proc/wmgmt/scram/trunk/scram/startup.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 13:56:56 $
# Last checked in by: $Author: starritt $
#

from __future__ import print_function
import sys
import logging
import logging.handlers
import click

from scram import program_name, __version__
import main

logger = logging.getLogger(__name__)

epilog = """

"""

logfile_help = """
Define the log file used for logging. If not specifed, then the \
SCRAM_LOG_FILE environment variable is used.
"""

loglevel_help = """
Sets the application's default logging level.
"""


def loglevel_choices():
    # TODO: Use logging API to create this list
    return ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


@click.command(epilog=epilog)
#
@click.option('--logfile',
              envvar='SCRAM_LOG_FILE',
              help=logfile_help)
#
@click.option("--loglevel",
              type=click.Choice(loglevel_choices()),
              envvar='SCRAM_LOG_LEVEL',
              default='WARNING',
              help=loglevel_help,
              show_default=True)
#
# TODO: Add config file/database connection
# TODO: Create an alarm log (as oppsosed to a scram application log)
#
def run(logfile, loglevel):

    if logfile is None or len(logfile) == 0:
        print ("Missing log file specification", file=sys.stderr)
        return 4

    # Configure the root logger and set up own logger
    #
    set_logging_paradigm(logfile, loglevel)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    print ("%s version %s" % (program_name, __version__), file=sys.stdout)
    sys.stdout.flush()

    logger.info("%s version %s" % (program_name, __version__))

    main.execute()

    # We always log start and stop.
    #
    logger.info("%s complete\n" % program_name)
    print ("%s complete\n" % program_name)
    return 0


# -----------------------------------------------------------------------------
#
def set_logging_paradigm(filename, loglevel):
    """Set up the root logger"""

    root_logger = logging.getLogger()

    # Set up logging
    #
    log_format = "%s%s" % ("%(asctime)s.%(msecs)03d %(levelname)-7s ",
                           "%(lineno)4d %(module)-20s %(message)s")

    formatter = logging.Formatter(fmt=log_format, datefmt="%Y-%m-%d %H:%M:%S")

    trfh = logging.handlers.TimedRotatingFileHandler(filename,
                                                     when='D',
                                                     interval=1,
                                                     backupCount=100)
    trfh.setFormatter(formatter)

    root_logger.addHandler(trfh)

    # Convert string to level
    level = logging.getLevelName(loglevel)
    root_logger.setLevel(level)


# end
