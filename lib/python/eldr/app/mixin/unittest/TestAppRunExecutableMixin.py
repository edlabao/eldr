"""
Unit tests for the AppRunExecutableMixin class.
"""

import os
import sys
import unittest

##
## BOOTSTRAP: BEGIN
##
## Bootstrapping code to ensure we can find all the right modules. All other
## local imports should be done after this block.
##
_path = os.path.realpath(__file__)
sys.path.insert(0, _path[:_path.find("/eldr/app")])
##
## BOOTSTRAP: END
##

from eldr.app import App
from eldr.app.codes import AppStatusOkay
from eldr.app.errors import AppRunExecutableError
from eldr.app.mixin.runexecutable import AppRunExecutableMixin


class TestApp(AppRunExecutableMixin, App):

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

        cmd = ["ls", "-l", "./"]
        app = TestApp()
        for line in app.run_executable(cmd):
            pass
        self.assertEqual(app.executable_status, AppStatusOkay)


    def test_run_executable2(self):
        """
        Verify a failed ls command.
        """

        cmd = ["ls", "-l", "/foo"]
        app = TestApp()

        try:
            no_such_file = False
            for line in app.run_executable(cmd):
                if "No such file" in line:
                    no_such_file = True
        except AppRunExecutableError:
            self.assertEqual(app.executable_status, 1)
            self.assertTrue(no_such_file)


if __name__ == "__main__":
    unittest.main()
