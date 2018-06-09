"""
Mixin that adds convenience methods for running an executable. As a mixin, this
module is not meant to be used as a standalone and requires certain members and
methods from the App base class to be defined.
"""

import collections
import os
import sys

from subprocess import Popen, PIPE, STDOUT
from eldr.app.codes import AppStatusOkay
from eldr.app.errors import AppRunExecutableError


class AppRunExecutableMixin(object):
    """
    Application framework mixin class that adds executable call support.

    """

    def __init__(self, *args, **kwargs):

        super(AppRunExecutableMixin, self).__init__(*args, **kwargs)

        self._executable_status = AppStatusOkay

    @property
    def executable_status(self):
        """
        *Property.* Return the current executable exit status value.
        """
        return self._executable_status

    def run_executable(self, cmd, **kwargs):
        """
        * *cmd* (list): List instance in which the first element is the path of
          an executable to run and remaining elements are arguments.
        * *kwargs* (dict): Dictionary containing key/value pairs of extra
          parameters to pass the :class:`subprocess.Popen()` command. There are
          also a few mixin parameters that can be passed via `kwargs` that are
          stripped before passing to :class:`subprocess.Popen()`

          * *expected_statuses* (list): Integer list of values that are
            acceptable exit codes for the executable (default=[0]).
        """

        # Reset the exit status.
        self._executable_status = AppStatusOkay

        # Set a default list of expected exit status values.
        expected_statuses = [AppStatusOkay]

        # Store the last few lines of output in case we need to log an error.
        output = collections.deque(maxlen=10)

        # If there is a kwarg called "expected_values", extract it.
        if "expected_statuses" in kwargs:
            expected_statuses = kwargs["expected_statuses"]
            del(kwargs["expected_statuses"])

        # Build the kwargs for the popen command. There are certain options that
        # we always want set, but we extend it with any user-provided kwargs.
        popen_kwargs = {"bufsize": 1, "stderr": STDOUT, "stdout": PIPE}
        popen_kwargs.update(kwargs)

        # Run the command with popen, redirecting sterr to stdout and piping the
        # output so it can be captured.
        p = Popen(cmd, **popen_kwargs)

        # Run the command and capture stdout and yield the output a line at a
        # time to the caller.
        pout = p.stdout
        while True:
            line = pout.readline()
            if line != "":
                output.append(line.rstrip())
                yield line
            else:
                break

        # Wait for the process to complete.
        p.wait()

        # Capture the exit status of the executable.
        self._executable_status = p.returncode

        # Check the exit status and raise an exception if it is not an expected
        # value.
        if self._executable_status not in expected_statuses:

            # Build the error message.
            msg = ["Executable returned unexpected exit status:",
                   "- command: %s" % " ".join(cmd),
                   "- exit status: {}".format(self._executable_status),
                   "- output:"]
            for line in output:
                msg.append("  > %s" % line)

            # Raise the exception with the error message.
            raise AppRunExecutableError("\n".join(msg))
