"""
Unit tests for the App class.
"""

import logging
import os
import sys
import time
import unittest

##
# BOOTSTRAP: BEGIN
#
# Bootstrapping code to ensure we can find all the right modules. All other
# local imports should be done after this block.
##
_path = os.path.realpath(__file__)
sys.path.insert(0, _path[:_path.find("/jaraf/app")])
##
# BOOTSTRAP: END
##

from jaraf.app import App
from jaraf.app.codes import AppStatusOkay, AppStatusError
from jaraf.app.errors import AppArgumentError


class TestApp(App):
    """
    Test Application that subclasses from the base App class.
    """

    def __init__(self, *args, **kwargs):

        super(TestApp, self).__init__(*args, **kwargs)

        # Flags that track if specific methods were called.
        self.add_arguments_called = False
        self.main_called = False
        self.process_arguments_called = False

        self.test_arg = None
        self.test_flag = False

    def add_arguments(self, parser):
        self.add_arguments_called = True
        parser.add_argument("--test-arg", dest="test_arg")
        parser.add_argument("--test-flag", action="store_true", dest="test_flag")

    def main(self):
        self.main_called = True

    def main_app_error(self):
        raise AppArgumentError

    def main_error(self):
        raise RuntimeError

    def process_arguments(self, args, arg_extras):
        self.process_arguments_called = True
        if args.test_arg is not None:
            self.test_arg = args.test_arg
        if args.test_flag is not None:
            self.test_flag = args.test_flag


class Test(unittest.TestCase):

    def test_add_arguments1(self):
        """
        Verify the base App class add_arguments() method exists and is a no-op.
        """
        app = App()
        app.add_arguments(None)

    def test_add_arguments2(self):
        """
        Verify that subclasses can add new arguments.
        """
        app = TestApp(silent=True)
        app.run()
        self.assertTrue(app.add_arguments_called)

    def test_execute1(self):
        """
        Verify the base App class execute() method raises a NotImplementedError.
        """
        app = App()
        self.assertRaises(NotImplementedError, app.main)

    def test_execute2(self):
        """
        Verify the subclass' execute method is called.
        """
        app = TestApp(silent=True)
        app.run()
        self.assertTrue(app.main_called)

    def test_get_log_handler1(self):
        """
        Verify the default get_log_handler() method returns a StreamHandler if
        the silent flag is False.
        """
        app = App()
        handler = app.get_log_handler(False)
        self.assertTrue(isinstance(handler, logging.StreamHandler))

    def test_get_log_handler2(self):
        """
        Verify the default get_log_handler() method returns a NullHandler if the
        silent flag is True.
        """
        app = App()
        handler = app.get_log_handler(True)
        self.assertTrue(isinstance(handler, logging.NullHandler))

    def test_init1(self):
        """
        Verify that base App members have the expected default values.
        """

        app = App()
        self.assertEqual(app._log_level, logging.INFO)
        self.assertEqual(app._status, AppStatusOkay)
        self.assertFalse(app._silent)

    def test_init2(self):
        """
        Verify that base App member values are set correctly when parameters
        are passed to the constructor.
        """
        app = App(silent=True, log_level="DEBUG")
        self.assertTrue(app._silent)
        self.assertTrue(app._log_level, logging.DEBUG)

    def test_name_to_log_level1(self):
        """
        Verify the name_to_log_level() function correctly maps log level names
        to the appropriate logging level code.
        """

        app = App()

        self.assertEqual(app.name_to_log_level("CRIT"), logging.CRITICAL)
        self.assertEqual(app.name_to_log_level("CRITICAL"), logging.CRITICAL)
        self.assertEqual(app.name_to_log_level("DEBUG"), logging.DEBUG)
        self.assertEqual(app.name_to_log_level("ERROR"), logging.ERROR)
        self.assertEqual(app.name_to_log_level("INFO"), logging.INFO)
        self.assertEqual(app.name_to_log_level("WARN"), logging.WARN)

    def test_name_to_log_level2(self):
        """
        Verify the default logging level if the specified log level name is not
        recognized.
        """
        app = App()
        self.assertEqual(app.name_to_log_level("TEST"), None)
        self.assertEqual(app.name_to_log_level("TEST", logging.DEBUG),
                         logging.DEBUG)

    def test_process_arguments1(self):
        """
        Verify the base App class process_arguments() method exists and is a
        no-op.
        """
        app = App()
        app.process_arguments(None, None)

    def test_process_arguments2(self):
        """
        Verify that base App arguments are processed correctly.
        """
        app = TestApp(silent=True)
        app.run(args=["--log-level", "DEBUG", "--silent"])
        self.assertEqual(app.log_level, logging.DEBUG)
        self.assertEqual(app._silent, True)

    def test_process_arguments3(self):
        """
        Verify that a bad log level argument doesn't get applied and that the
        default value remains in effect.
        """
        app = TestApp(silent=True)
        app.run(args=["--log-level", "DUBUG"])
        self.assertEqual(app.log_level, logging.INFO)

    def test_process_arguments4(self):
        """
        Verify that subclass arguments are processed correctly.
        """
        app = TestApp(silent=True)
        app.run(args=["--test-arg", "foobar", "--test-flag"])

        self.assertTrue(app.process_arguments_called)
        self.assertEqual(app.test_arg, "foobar")
        self.assertTrue(app.test_flag)

    def test_run1(self):
        """
        Verify that AppError exceptions are handled correctly.
        """
        app = TestApp(silent=True)

        # Monkey patch our app object by pointing the main() method to the
        # test main method that raises an AppArgumentError and run the app.
        app.main = app.main_app_error
        app.run()

        # Running an main method that raises an AppError should not raise an
        # exception nor set the status.
        self.assertEqual(app.status, AppStatusOkay)

    def test_run2(self):
        """
        Verify that general application exceptions are handled correctly.
        """
        app = TestApp(silent=True)

        # Monkey patch our app object by pointing the main() method to the
        # test main method that raises a RuntimeError and run the app.
        app.main = app.main_error
        app.run()

        # Running an main method that raises a non-AppError should set an
        # error status.
        self.assertEqual(app.status, AppStatusError)


if __name__ == "__main__":
    unittest.main()
