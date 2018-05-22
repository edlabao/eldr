"""
Application framework package.
"""

import argparse
import logging
import os
import pwd
import sys
import time
import traceback

from eldr.app.codes import AppStatusOkay, AppStatusError
from eldr.app.errors import AppError


class App(object):
    """
    Application abstract base class.
    """

    #__metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        """
        Initialization method for the App class.

        Certain App parameters can be overridden at object instantiation time by
        passing keyword arguments to the constructor.
        """

        # Process information.
        self._app_name = self.__class__.__name__.lower()
        self._program_name = os.path.basename(sys.argv[0])
        self._user = pwd.getpwuid(os.getuid()).pw_name

        # Argument parsing.
        self._args = None
        self._arg_extras = []
        self._arg_parser = argparse.ArgumentParser()

        # Logging parameters.
        self.log = logging
        self._log_level = self.name_to_log_level(kwargs.get("log_level", "INFO"))
        self._silent = kwargs.get("silent", False)

        # Application execution start time.
        self._start_time = time.time()

        # Application exit code.
        self._status = AppStatusOkay

    def add_arguments(self, parser):
        """
        Optional method that can be defined by subclasses to add support for
        additional command-line arguments.

        This method is passed an ArgumentParser object that is used to add
        custom arguments via its add_argument() method. This method is only
        intended for adding new arguments. Actual processing of the arguments
        will be performed in the process_arguments() method.
        """
        pass

    def get_log_formatter(self):
        """
        Return a log formatter.
        """
        format_fields = ["%(asctime)s",
                         "%(levelname)s",
                         "%(message)s"]
        return logging.Formatter(" ".join(format_fields))

    def get_log_handler(self, silent):
        """
        Return a log handler.
        """
        if silent:
            return logging.NullHandler()
        else:
            return logging.StreamHandler(sys.stdout)

    def init_logging(self):
        """
        Configure output logging.
        """

        self.log = logging.getLogger(self._app_name)
        self.log.setLevel(self._log_level)

        formatter = self.get_log_formatter()
        handler = self.get_log_handler(self._silent)
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

    def log_exception(self):
        """
        Log the current stack trace.
        """
        for line in traceback.format_exc().split("\n"):
            if line:
                self.log.error("> {}".format(line))

    @property
    def log_level(self):
        """
        Return the current logging level.
        """
        return self._log_level

    def main(self):
        """
        Entry point for the application subclass and must be implemented.
        """
        raise NotImplementedError

    def process_arguments(self, args, arg_extras):
        """
        Optional method that can be defined by subclasses to add support for
        additional command-line arguments.

        This method is passed the Namespace object returned by the
        ArgParser.parse_args().
        """
        pass

    def run(self, args=None):
        """
        Application entry point.

        Unlike the execute() method, subclasses should only call this method and
        not implement it as it performs application initialization and
        ultimately calls the execute() method.

        :Parameters:
            args : List of arguments to process instead of sys.argv.

        :Returns:
            status : Application exit code.
        """

        try:
            # Add application arguments, first calling the base _add_arguments()
            # method then the optional add_arguments() method.
            self._add_arguments()
            self.add_arguments(self._arg_parser)

            # Process application options, first calling the base
            self._process_arguments(args)
            self.process_arguments(self._args, self._arg_extras)

            # Initialize logging for the application.
            self.init_logging()

            # Output a header and execute the application.
            self.log.info("-" * 72)
            self.main()

        except AppError:
            # When an AppError is raised, assume that the subclass has already
            # handled the error (e.g. logged the error, set the status code) so
            # do nothing.
            pass

        except Exception, err:

            # When a non-AppError exception is raised, set the status and log
            # the error.
            self._status = AppStatusError

            # An exception can occur before logging has been initialized. Check
            # for the log member and initialize it with the root logging object
            # if it doesn't exist.
            if "log" not in dir(self):
                self.log = logging

            self.log.error("Unhandled exception: {}".format(err))
            self.log_exception()

        # Output a footer and return the application status code.
        self.log.info("FINISHED {}".format(self._program_name))
        self.log.info("- Exit status: {}".format(self.status))

        return self.status

    @property
    def status(self):
        """
        Return the current application status code.
        """
        return self._status

    def _add_arguments(self):
        """
        Add base App command-line arguments.
        """
        self._arg_parser.add_argument("--log-level", "-l",
                                      action="store",
                                      dest="log_level")

        self._arg_parser.add_argument("--silent",
                                      action="store_true",
                                      dest="silent")

    def _process_arguments(self, args=None):
        """
        Process base App command-line arguments.
        """

        (self._args, self._arg_extras) = self._arg_parser.parse_known_args(args)

        # Logging level.
        if self._args.log_level is not None:
            log_level = self.name_to_log_level(self._args.log_level)
            if log_level is not None:
                self._log_level = log_level

        # Silent flag.
        if self._args.silent:
            self._silent = True

    @staticmethod
    def name_to_log_level(level_name, default=None):
        """
        Convert the specified logging level name to the corresponding logging
        constant (e.g. logging.DEBUG, logging.WARN).

        If the specified level_name is not recognized, the specified optional
        default is returned. If no default is specified and the level_name is
        not recognized, None is returned.

        :Parameters:
            level_name : Logging level name to convert to a logging level code.
            default : Logging level to return if the name is not supported.

        :Returns:
            level : Logging level constant.
        """

        level = default

        # Convert the level_name to upper case and find the matching logging
        # level for it.
        level_name = level_name.upper()
        if level_name == "DEBUG":
            level = logging.DEBUG
        elif level_name == "INFO":
            level = logging.INFO
        elif level_name in ("WARN", "WARNING"):
            level = logging.WARN
        elif level_name == "ERROR":
            level = logging.ERROR
        elif level_name in ("CRIT", "CRITICAL"):
            level = logging.CRITICAL

        return level
