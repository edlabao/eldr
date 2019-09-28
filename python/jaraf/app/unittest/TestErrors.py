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

from jaraf.app.codes import (AppStatusArgumentError,
                             AppStatusError,
                             AppStatusInitializationError,
                             AppStatusOkay)
from jaraf.app.errors import (AppArgumentError,
                              AppError,
                              AppInitializationError)


class Test(unittest.TestCase):

    def test_apperror(self):
        """
        Verify a plain AppError exception.
        """

        try:
            raise AppError
        except AppError as err:
            self.assertEqual(err.status, AppStatusError)

    def test_apperror_status(self):
        """
        Verify an AppError exception with a custom status.
        """

        try:
            raise AppError(status=123)
        except AppError as err:
            self.assertEqual(err.status, 123)

    def test_appargumenterror(self):
        """
        Verify a plain AppArgumentError exception.
        """

        try:
            raise AppArgumentError
        except AppArgumentError as err:
            self.assertEqual(err.status, AppStatusArgumentError)

    def test_appargumenterror_status(self):
        """
        Verify an AppArgumentError exception with a custom status.
        """

        try:
            raise AppArgumentError(status=123)
        except AppArgumentError as err:
            self.assertEqual(err.status, 123)

    def test_appinitialization_error(self):
        """
        Verify a plain AppInitializationError exception.
        """

        try:
            raise AppInitializationError
        except AppInitializationError as err:
            self.assertEqual(err.status, AppStatusInitializationError)

    def test_appinitialization_status(self):
        """
        Verify an AppInitializationError exception with a custom status.
        """

        try:
            raise AppInitializationError(status=123)
        except AppInitializationError as err:
            self.assertEqual(err.status, 123)


if __name__ == "__main__":
    unittest.main()
