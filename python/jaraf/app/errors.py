"""
Application error classes.
"""

from jaraf.app.codes import (AppStatusArgumentError,
                             AppStatusError,
                             AppStatusInitializationError,
                             AppStatusOkay)


class AppError(Exception):
    """
    Generic App exception.
    """

    def __init__(self, *args, **kwargs):
        super(AppError, self).__init__()
        self._status = kwargs.get("status", AppStatusError)

    @property
    def status(self):
        return self._status


class AppArgumentError(AppError):
    """
    Exception that should be raised if an error occurs while processing command-
    line arguments.
    """

    def __init__(self, *args, **kwargs):
        super(AppArgumentError, self).__init__(**kwargs)
        self._status = kwargs.get("status", AppStatusArgumentError)


class AppInitializationError(AppError):
    """
    Exception that should be raised if an error occurs while initializing the
    application.
    """

    def __init__(self, *args, **kwargs):
        super(AppInitializationError, self).__init__(**kwargs)
        self._status = kwargs.get("status", AppStatusInitializationError)
