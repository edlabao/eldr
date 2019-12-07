"""
Test suite for App tests.
"""

import os
import sys

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

import unittest

from TestApp import Test as TestApp
from TestErrors import Test as TestErrors


# Initialize a test suite and add all of the TestCases.
TestHandlerSuite = unittest.TestSuite()
TestHandlerSuite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestApp))
TestHandlerSuite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestErrors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
