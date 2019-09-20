"""
Mixin that adds support for logging application output to a log file. As a
mixin, this module is not meant to be used as a standalone and requires certain
members and methods from the App base class to be defined.

This class overloads the :meth:`~.App.get_log_formatter()`,
:meth:`~.App.get_log_handler()` and :meth:`~.App.init_logging()` methods of the
:class:`.App` base class so subclasses should not overload these themselves.

An instance of the :class:`~logging.handlers.TimedRotatingFileHandler` is
used to enable rotating log files at a specified time. There are a few
constructor parameters supported to allow customization of the log rotation
behavior:

* *log_backup_count* (int): Specify how many rotated log files to keep
  (default=6).
* *log_rotate_when* (str): Specify when to rotate the log file
  (default="MIDNIGHT"). Refer to the Python :mod:`logging.handlers`
  documentation for valid values.

::

    from jaraf.app import App
    from jaraf.app.mixin.logfile import AppLogFileMixin

    class MyApp(AppLogFileMixin, App):
        #
        # Define the rest of the class
        #

    if __name__ == "__main__":
        app = MyApp(log_backup_count=3, log_rotate_when="W0")

In the above example, the log is rotated once a week on Monday, and 3
backpups are kept plus the current log. This results in up to 4 log files
that cover the last month's worth of application logging.

"""

import datetime
import logging.handlers
import os
import socket
import sys

from jaraf.app.errors import AppInitializationError


class LogFileMixin(object):
    """
    Application framework mixin class that adds logfile support.
    """

    def __init__(self, *args, **kwargs):

        super(LogFileMixin, self).__init__(*args, **kwargs)

        # Process information used for the logging format.
        self._pid = os.getpid()
        self._hostname = socket.gethostname()

        # Logging parameters.
        self._log_backup_count = kwargs.get("log_backup_count", 7)
        self._log_base_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        self._log_rotate_when = kwargs.get("log_rotate_when", "MIDNIGHT")

        self._log_dir = None
        self._set_log_dir(kwargs.get("log_dir"))

        self._log_file = None
        self._set_log_file(kwargs.get("log_file"))

    def get_log_formatter(self):
        """
        Overload the get_log_formatter() method to provide additional context
        information in the logging output.
        """
        format_fields = ["%(asctime)s",
                         "[{}.{}]".format(self._hostname, self._pid),
                         "%(levelname)s",
                         "%(message)s"]
        return logging.Formatter(" ".join(format_fields))

    def get_log_handler(self):
        """
        Overload the get_log_handler() method to return a
        TimedRotatingLogHandler.
        """
        return logging.handlers.TimedRotatingFileHandler(self.log_file,
                                                         when=self._log_rotate_when,
                                                         backupCount=self._log_backup_count)

    def init_logging(self):
        """
        Overload the init_logging() method to initialize logging to an output
        log file.
        """

        # Create the output log first directory if it doesn't exist.
        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir, 0o777)

        except Exception as err:
            sys.stderr.write("**ERROR** Unable to create %s\n" % self.log_dir)
            sys.stderr.write("**ERROR** > %s\n" % err)
            raise AppInitializationError

        # Initialize the logger.
        self.log = logging.getLogger(self._app_name)
        self.log.setLevel(self._log_level)

        formatter = self.get_log_formatter()
        handler = self.get_log_handler()
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

        # Rotate the log if necessary.
        self._rotate_log(handler)

    @property
    def log_dir(self):
        """
        *Property.* Return the log directory.
        """
        return self._log_dir

    @property
    def log_file(self):
        """
        *Property.* Return the log file path.
        """
        return self._log_file

    def _add_arguments(self):
        """
        Add AppLogFileMixin command-line arguments.
        """

        super(LogFileMixin, self)._add_arguments()

        self._arg_parser.add_argument("--log-file",
                                      action="store",
                                      dest="log_file")

    def _process_arguments(self, args=None):
        """
        Process AppLogFileMixin command-line arguments.
        """

        super(LogFileMixin, self)._process_arguments(args)

        # Log file.
        self._set_log_file(self._args.log_file)

    @staticmethod
    def _rotate_log(log_handler):
        """
        Rotate the log before beginning, if necessary.

        Since the TimedRotatingFileHandler will only rotate logs if it is
        running at the time the rotate condition happens we explicitly check
        here. This is only guaranteed to work correctly, however, if the rotate
        condition is the default of "midnight".
        """
        if log_handler.when == "MIDNIGHT":
            mtime = os.stat(log_handler.baseFilename).st_mtime
            log_date = datetime.date.fromtimestamp(mtime)
            if str(log_date) != str(datetime.date.today()):
                log_handler.doRollover()

    def _set_log_dir(self, log_dir):
        """
        Set the log directory.
        """
        self._log_dir = log_dir
        if self._log_dir is None:
            self._log_dir = "{}/{}".format("/var/log", self._log_base_name)

    def _set_log_file(self, log_file):
        """
        Set the log file.

        In addition to setting the _log_file member, this will also set _log_dir
        if the specified log_file looks like an absolute path.
        """

        self._log_file = log_file

        # If the log file looks like an absolute path, also set the log
        # directory to the directory component of the log file path. If the log
        # file is not an absolute path, make it one by prefixing the log
        # directory to it if the directory is set.
        if self._log_file is not None:
            if self._log_file.startswith("/"):
                self._log_dir = os.path.dirname(self._log_file)
            elif self._log_dir is not None:
                self._log_file = "{}/{}".format(self._log_dir, self._log_file)

        # If the log file is not set, but the log directory is, set a default
        # log file path.
        elif self._log_dir is not None:
            self._log_file = "{}/{}.log".format(self.log_dir, self._app_name)
