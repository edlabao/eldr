"""
Application framework package.
"""

import argparse
import logging
import os
import pwd
import resource
import sys
import time
import traceback

from jaraf.app.codes import AppStatusOkay, AppStatusError
from jaraf.app.errors import AppError


class App(object):
    """
    Application abstract base class.::

        from jaraf.app import App

        class MyApp(App):
            #
            # Define the rest of the class
            #

        if __name__ == "__main__":
            app = App()
            app.run()

    Certain :class:`App` parameters can be overridden at object instantiation time
    by passing keyword arguments to the constructor.::

        app = MyApp(log_level="DEBUG", silent=True, log_level="DEBUG")

    """

    #__metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):

        # Process information.
        self._app_name = self.__class__.__name__.lower()
        self._program_name = os.path.basename(sys.argv[0])

        try:
            self._user = pwd.getpwuid(os.getuid()).pw_name
        except:
            self._user = os.environ.get("USER")

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
        *Virtual.* Optional method that can be defined by subclasses to add
        support for additional command-line arguments.

        This method is passed a **parser** parameter which is an instance of
        :class:`argparse.ArgumentParser` that is used to add custom arguments
        via :func:`argparse.ArgumentParser.add_argument()`. This method should
        only be used to add new arguments to the parser. Actual processing of
        the arguments should be performed in the :func:`App.process_arguments()`
        method.

        For example::

            def add_arguments(self, parser):
                parser.add_argument("--foo", dest="foo")
                parser.add_argument("--bar", action="store_true", dest="bar")

        """
        pass

    def get_log_formatter(self):
        """
        Return a log formatter object.

        The default log formatter :
        ``%(asctime)s %(levelname)s %(message)s``.

        *Returns*: An instance of :class:`logging.Formatter`.
        """
        format_fields = ["%(asctime)s",
                         "%(levelname)s",
                         "%(message)s"]
        return logging.Formatter(" ".join(format_fields))

    def get_log_handler(self, silent=False):
        """
        * *silent* (bool): If True, turn on silent mode.

        Return a log handler. By default an instance of
        :class:`logging.StreamHandler` that logs to :mod:`sys.stdout` is
        returned, but if ``silent=True``, then an instance of
        :class:`logging.NullHandler` is returned instead, and all logging is
        effectively silenced.

        Subclasses will generally never call this method directly since it is
        called as part of log initialization; however, a subclass may overload
        this method to return a custom logging handler if necessary.

        *Returns*: An instance of :class:`logging.Handler`
        """
        if silent:
            return logging.NullHandler()
        else:
            return logging.StreamHandler(sys.stdout)

    def init_logging(self):
        """
        Configure and initialize output logging. Subclasses should not call this
        method, but it is defined as a public method to allow customization if
        needed.
        """

        self.log = logging.getLogger(self._app_name)
        self.log.setLevel(self._log_level)

        formatter = self.get_log_formatter()
        handler = self.get_log_handler(self._silent)
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

    def log_exception(self):
        """
        Convenience method that can be used to log the current exception. This
        is typically used inside an except block, and ensures that the exception
        is logged with the proper formatting::

            try:
                # Do something that raises an exception.
            except Exception:
                # Handle the exception then log the stack trace.
                self.log_exception()

        """
        for line in traceback.format_exc().split("\n"):
            if line:
                self.log.error("> {}".format(line))

    @property
    def log_level(self):
        """
        *Property.* Return the current logging level.
        """
        return self._log_level

    def main(self):
        """
        *Virtual.* Entry point for the application subclass and must be
        implemented.
        """
        raise NotImplementedError

    def process_arguments(self, args, arg_extras):
        """
        *Virtual*. Optional method that can be defined by subclasses to add
        support for additional command-line arguments.

        This method is passed the **args** parameter which is a
        :class:`Namespace` object returned by
        :func:`argparse.ArgParser.parse_args()`. In addition, if there were any
        unsupported arguments passed to the program that were not parsed, these
        are added to the **arg_extras** list.

        For example::

            def process_arguments(self, args, arg_extras):
                if args.foo is not None:
                    self.foo = args.foo
                if args.bar is not None:
                    self.bar = args.bar
                self.baz_list = arg_extras

        """
        pass

    def run(self, args=None):
        """
        * *args* (dict): If an args parameter is specified, it is parsed for
          command-line options rather than :mod:`sys.argv`. This is primarily
          used for testing.

        Subclasses call this method to start the application. This should only
        be called and not overridden by applications as this performs
        initialization tasks to prepare the application prior to calling the
        :func:`App.main()` method.

        *Returns:* An integer representing the application exit code.
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
            self.log.info("STARTING {}".format(self._program_name))
            self.main()

        except AppError:
            # When an AppError is raised, assume that the subclass has already
            # handled the error (e.g. logged the error, set the status code) so
            # do nothing.
            pass

        except Exception as err:

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

        # Calculate some run stats.
        elapsed_time = time.time() - self._start_time
        rusage_self = resource.getrusage(resource.RUSAGE_SELF)
        rusage_child = resource.getrusage(resource.RUSAGE_CHILDREN)

        # Calculate cpu time as combined user and system times.
        cpu_time = rusage_self.ru_utime + rusage_self.ru_stime \
            + rusage_child.ru_utime + rusage_self.ru_stime

        # RSS units are in kb on Linux but bytes on OSX.
        units = float(2**10)
        if sys.platform == "darwin":
            units = float(2**20)
        max_rss = float(rusage_self.ru_maxrss + rusage_child.ru_maxrss) / units

        # Output a footer and return the application status code.
        self.log.info("FINISHED {}".format(self._program_name))
        self.log.info("- exit status: {}".format(self.status))
        self.log.info("- elapsed time: {:0.5f} secs".format(elapsed_time))
        self.log.info("- cpu time: {:0.5f} secs".format(cpu_time))
        self.log.info("- max rss: {:0.5f} MiB".format(max_rss))

        return self.status

    @property
    def status(self):
        """
        *Property.* Return the current application status code.
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
        * *level_name* (str): Logging level name to convert to a logging level
          code.
        * *default* (int): Logging level to return if the name is not
          supported.

        Convert the specified logging level name to the corresponding logging
        constant (e.g. :func:`logging.DEBUG`, :func:`logging.WARN`). If the
        specified level_name is not recognized, the specified optional default
        is returned. If no default is specified and the level_name is not
        recognized, :class:`None` is returned.

        Valid level names:

        * DEBUG
        * INFO
        * WARN
        * WARNING
        * ERROR
        * CRIT
        * CRITICAL

        *Returns:* An integer corresponding to a logging level.
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
