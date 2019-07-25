"""
Unit tests for the AppLogFileMixin class.
"""

import logging
import os
import re
import shutil
import sys
import tempfile
import unittest

##
# BOOTSTRAP: BEGIN
#
# Bootstrapping code to ensure we can find all the right modules. All other
# local imports should be done after this block.
##
_path = os.path.realpath(__file__)
sys.path.insert(0, _path[:_path.find("/eldr/app")])
##
# BOOTSTRAP: END
##

from eldr.app import App
from eldr.app.errors import AppInitializationError
from eldr.app.mixin.logfile import LogFileMixin


class TestApp(LogFileMixin, App):

    def __init__(self, *args, **kwargs):

        super(TestApp, self).__init__(*args, **kwargs)

        # Flog to indicate if our execute() method was called.
        self.execute_called = False

    def execute(self):
        self.execute_called = True


class Test(unittest.TestCase):

    def test_arguments1(self):
        """
        Verify that adding arguments with the "protected" method
        _add_arguments() correctly appends new arguments and that the base App
        arguments are still valid.
        """
        # Initialize a temporary directory.
        test_dir = tempfile.mkdtemp()
        test_file = "{}/testapp.log".format(test_dir)

        try:
            # Initialize the app, passing in the test directory for the log_dir
            # as-is. The test directory will have been created by the tempfile
            # module for us.
            app = TestApp()
            app.run(args=["--log-file", test_file,
                          "--log-level", "DEBUG",
                          "--silent"])

            self.assertEqual(app.log_file, test_file)
            self.assertEqual(app._log_level, logging.DEBUG)
            self.assertTrue(app._silent)

        finally:
            # Remove the log handler we generated (log handlers are singletons
            # so subsequent tests may have unexpected results if we don't remove
            # them after each test) and remove the temp directory we created.
            app.log.handlers[0].close()
            app.log.removeHandler(app.log.handlers[0])
            shutil.rmtree(test_dir)

    def test_arguments2(self):
        """
        Verify that setting the log directory via a constructor parameter and a
        log file that is not a path via command line arguments results in a log
        file with the correct absolute path.
        """
        # Initialize a temporary directory.
        test_dir = tempfile.mkdtemp()
        test_file = "testapp.log"

        try:
            # Initialize the app, passing in the test directory for the log_dir
            # as-is. The test directory will have been created by the tempfile
            # module for us.
            app = TestApp(log_dir=test_dir)
            app.run(args=["--log-file", test_file])

            self.assertEqual(app.log_dir, test_dir)
            self.assertEqual(app.log_file, "{}/{}".format(test_dir, test_file))

        finally:
            # Remove the log handler we generated (log handlers are singletons
            # so subsequent tests may have unexpected results if we don't remove
            # them after each test) and remove the temp directory we created.
            app.log.handlers[0].close()
            app.log.removeHandler(app.log.handlers[0])
            shutil.rmtree(test_dir)

    def test_arguments3(self):
        """
        Verify that specifying a log file with an absolute path via command-line
        arguments will override a directory set via constructor parameter.
        """
        # Initialize a temporary directory.
        test_dir = tempfile.mkdtemp()
        test_file = "{}/testapp.log".format(test_dir)

        try:
            # Initialize the app, passing in the test directory for the log_dir
            # as-is. The test directory will have been created by the tempfile
            # module for us.
            app = TestApp(log_dir="/foo/bar")
            app.run(args=["--log-file", test_file])

            self.assertEqual(app.log_dir, test_dir)
            self.assertEqual(app.log_file, test_file)

        finally:
            # Remove the log handler we generated (log handlers are singletons
            # so subsequent tests may have unexpected results if we don't remove
            # them after each test) and remove the temp directory we created.
            app.log.handlers[0].close()
            app.log.removeHandler(app.log.handlers[0])
            shutil.rmtree(test_dir)

    def test_init1(self):
        """
        Verify default logging parameters.
        """

        # Because the specific default log directory and file path will depend
        # on how this test is run (e.g. directly or via a suite like TestAll.py)
        # we validate their values by matching them against a regex.
        re_dir = re.compile("^\/var\/log\/[^\/]+$")
        re_file = re.compile("^\/var\/log\/[^\/]+\/[^\/+]+.log$")

        app = TestApp()
        self.assertEqual(app._log_backup_count, 7)
        self.assertTrue(re_dir.match(app._log_dir))
        self.assertTrue(re_file.match(app._log_file))
        self.assertEqual(app._log_rotate_when, "MIDNIGHT")

    def test_init2(self):
        """
        Verify setting parameters at object construction.
        """

        app = TestApp(log_backup_count=30,
                      log_dir="/foo",
                      log_file="bar.log",
                      log_rotate_when="W6")

        self.assertEqual(app._log_backup_count, 30)
        self.assertEqual(app._log_dir, "/foo")
        self.assertEqual(app._log_file, "/foo/bar.log")
        self.assertEqual(app._log_rotate_when, "W6")

    def test_init3(self):
        """
        Verify that setting base App parameters at object construction is still
        working properly.
        """
        app = TestApp(log_level="DEBUG", silent=True)
        self.assertEqual(app._log_level, logging.DEBUG)
        self.assertTrue(app._silent)

    def test_init_logging1(self):
        """
        Verify that the log directory is created correctly.
        """

        # Initialize a temporary directory. We append a subdirectory to the path
        # because the tempfile library actually creates the temp file directory,
        # but we need to pass a non-existent directory to the application.
        temp_root = tempfile.mkdtemp()
        test_dir = "{}/test".format(temp_root)

        try:
            # Initialize the app, passing in the test directory for the log_dir
            # as-is. The test directory will have been created by the tempfile
            # module for us.
            app = TestApp(log_dir=test_dir)
            app.init_logging()

            self.assertEqual(app.log_dir, test_dir)
            self.assertTrue(os.path.exists(app.log_dir))

        finally:
            # Remove the log handler we generated (log handlers are singletons
            # so subsequent tests may have unexpected results if we don't remove
            # them after each test) and remove the temp directory we created.
            app.log.handlers[0].close()
            app.log.removeHandler(app.log.handlers[0])
            shutil.rmtree(temp_root)

    def test_init_logging2(self):
        """
        Verify the logger object is initialized correctly.
        """

        # Initialize a temporary directory.
        test_dir = tempfile.mkdtemp()

        try:
            # Initialize the app, passing in the test directory for the log_dir
            # as-is. The test directory will have been created by the tempfile
            # module for us.
            app = TestApp(log_dir=test_dir, log_level="DEBUG")
            app.init_logging()

            self.assertEqual(app.log.getEffectiveLevel(), logging.DEBUG)
            self.assertTrue(isinstance(app.log.handlers[0],
                                       logging.handlers.TimedRotatingFileHandler))

        finally:
            # Remove the log handler we generated (log handlers are singletons
            # so subsequent tests may have unexpected results if we don't remove
            # them after each test) and remove the temp directory we created.
            app.log.handlers[0].close()
            app.log.removeHandler(app.log.handlers[0])
            shutil.rmtree(test_dir)

    def test_init_logging3(self):
        """
        Verify that a failure to create the log directory is handled correctly.
        """

        # Set a test directory that doesn't exist and that cannot actually be
        # created.
        test_dir = "/dev/null/test"

        # An exception raised during init_logging will write an error message to
        # stderr, so temporarily replace stderr with file handle to devnull.
        devnull = open(os.devnull, "a")
        orig_stderr = sys.stderr
        sys.stderr = devnull

        # Attempting to initialize logging should raise an exception because of
        # a permission denied error.
        app = TestApp(log_dir=test_dir)
        self.assertRaises(AppInitializationError, app.init_logging)

        # Clean up the devnull hack.
        sys.stderr = orig_stderr
        devnull.close()

    def test_init_logging4(self):
        """
        Verify the logger object is initialized correctly when a different
        rotate when parameter is specified.
        """

        # Initialize a temporary directory.
        test_dir = tempfile.mkdtemp()

        try:
            # Initialize the app, passing in the test directory for the log_dir
            # as-is. The test directory will have been created by the tempfile
            # module for us.
            app = TestApp(log_dir=test_dir, log_rotate_when="W6")
            app.init_logging()

            self.assertEqual(app.log.handlers[0].when, "W6")

        finally:
            # Remove the log handler we generated (log handlers are singletons
            # so subsequent tests may have unexpected results if we don't remove
            # them after each test) and remove the temp directory we created.
            app.log.handlers[0].close()
            app.log.removeHandler(app.log.handlers[0])
            shutil.rmtree(test_dir)

    def test_log_dir1(self):
        """
        Verify the return value of the log_dir property for a default app
        object.
        """

        # Because the specific default log directory will depend on how this
        # test is run (e.g. directly or via a suite like TestAll.py) we validate
        # its value by matching it against a regex.
        re_dir = re.compile("^\/var\/log\/[^\/]+$")

        app = TestApp()
        self.assertTrue(re_dir.match(app._log_dir))

    def test_log_dir2(self):
        """
        Verify the return value of the log_dir property if a log_dir parameter
        is passed to the constructor.
        """
        app = TestApp(log_dir="/foo")
        self.assertEqual(app.log_dir, "/foo")

    def test_log_file1(self):
        """
        Verify the return value of the log_file property for a default app
        object.
        """

        # Because the specific default log file path will depend on how this
        # test is run (e.g. directly or via a suite like TestAll.py) we validate
        # its value by matching it against a regex.
        re_file = re.compile("^\/var\/log\/[^\/]+\/[^\/+]+.log$")

        app = TestApp()
        self.assertTrue(re_file.match(app._log_file))

    def test_log_file2(self):
        """
        Verify the return value of the log_file property if a log_file parameter
        is passed to the constructor.
        """
        app = TestApp(log_file="/foo/bar.log")
        self.assertEqual(app.log_file, "/foo/bar.log")


if __name__ == "__main__":
    unittest.main()
