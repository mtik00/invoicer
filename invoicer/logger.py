import os
import sys
import logging


APPDIR = os.path.abspath(os.path.dirname(__file__))


def get_logger(name=None, screen_level=logging.INFO,
               logfile_path=None, logfile_level=logging.DEBUG,
               logfile_mode="ab"):
    """Returns a logging object.

    You should use the parameterized function once to initialize
    the logger.  Subsequent calls should use ``get_logger()`` to
    use the common logging object.
    :param str name: The name of the logger; defaults to the script name
    :param int screen_level: The level of the screen logger
    :param str logfile_path: The path of the log file, if any
    :param int logfile_level: The level of the file logger
    :param str logfile_mode: The file mode of the file logger

    :rtype: logging.logger
    :returns: A common logger for a project
    """
    if not name:
        name = os.path.splitext(os.path.basename(__file__))[0]

    _format = "%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s"
    _logger = logging.getLogger(name)
    _logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    screen_formatter = logging.Formatter(_format)
    ch.setFormatter(screen_formatter)
    ch.setLevel(screen_level)
    _logger.addHandler(ch)

    if logfile_path:
        logfile_formatter = logging.Formatter(_format)
        fh = logging.FileHandler(logfile_path, logfile_mode)
        fh.setLevel(logfile_level)
        fh.setFormatter(logfile_formatter)
        _logger.addHandler(fh)

    return _logger


# I'm cheating a little bit here.  This allows me to run the app directly on
# my Windows machine to make debugging a little bit easier.  Normally, though,
# the app is run on Ubuntu.
if "lin" in sys.platform:
    LOGGER = get_logger(name="invoicer-debug", logfile_path="/var/log/invoicer/debug.log")
    AUTH_LOG = get_logger(name="invoicer-auth", logfile_path="/var/log/invoicer/auth.log")
else:
    if not os.path.isdir(os.path.join(APPDIR, "..", "log")):
        os.makedirs(os.path.join(APPDIR, "..", "log"))

    LOGGER = get_logger(name="invoicer-debug", logfile_path=os.path.join(APPDIR, "..", "log", "debug.log"))
    AUTH_LOG = get_logger(name="invoicer-auth", logfile_path=os.path.join(APPDIR, "..", "log", "auth.log"))
