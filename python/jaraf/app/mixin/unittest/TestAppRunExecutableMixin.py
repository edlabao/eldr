"""
Unit tests for the AppRunExecutableMixin class.
"""

import os
import sys
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
from jaraf.app.codes import AppStatusOkay
from jaraf.app.mixin.runexecutable import RunExecutableMixin
from jaraf.app.mixin.runexecutable import RunExecutableError


class TestApp(RunExecutableMixin, App):

    def __init__(self, *args, **kwargs):

        super(TestApp, self).__init__(*args, **kwargs)


class Test(unittest.TestCase):

    def test_init(self):
        """
        Verify default run executable parameters.
        """
        app = TestApp()
        self.assertEqual(app.executable_status, AppStatusOkay)

    def test_run_executable1(self):
        """
        Verify a successful ls command.
        """

        # Grab a filename from the current directory to test against and
        # and initialize the file_seen test flag to False.
        test_file = os.listdir("./")[0]
        file_seen = False

        # Run a test ls command and validate that it ran successfully meaning
        # that it exited with a non-zero exit status and that it actually listed
        # a test file we're looking for.
        cmd = ["ls", "-Al", "./"]
        app = TestApp()
        for line in app.run_executable(cmd):
            # If the current output line containts the test file we're looking
            # for, set the file_seen test flag to True.
            if test_file in line:
                file_seen = True

        self.assertEqual(app.executable_status, AppStatusOkay)
        self.assertTrue(file_seen)

    def test_run_executable2(self):
        """
        Verify a failed ls command.
        """

        cmd = ["ls", "-l", "/foo"]
        app = TestApp()

        # Run a test ls command against a non-existent file. This should throw
        # an exception. We don't use self.assertRaises() here because the
        # run_executable() is a generator and only works correctl if it is used
        # as an iterable.
        try:
            no_such_file = False
            for line in app.run_executable(cmd):
                if "No such file" in line:
                    no_such_file = True

        except RunExecutableError:
            self.assertTrue(app.executable_status > 0)
            self.assertTrue(no_such_file)

    def test_run_executable3(self):
        """
        Verify a custom exit status code.
        """

        # Run the false command which exits with a status code of 1.
        cmd = ["false"]
        app = TestApp()
        for line in app.run_executable(cmd, expected_statuses=[1]):
            pass
        self.assertEqual(app.executable_status, 1)


if __name__ == "__main__":
    unittest.main()
