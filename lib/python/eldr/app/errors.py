"""
Application error classes.
"""


class AppError(Exception):
    """
    Generic App exception.
    """
    pass


class AppArgumentError(AppError):
    """
    Exception that should be raised if an error occurs while processing command-
    line arguments.
    """
    pass


class AppInitializationError(AppError):
    """
    Exception that should be raised if an error occurs while initializing the
    application.
    """
    pass


class AppRunExecutableError(AppError):
    """
    Exception that should be raised if an executable is run and exits with an
    unexpected exit status.
    """
    pass
