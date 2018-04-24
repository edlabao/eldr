"""
Application framework mixin that adds convenience methods for running an
executable.
"""

import collections
import os
import sys

from subprocess import Popen, PIPE, STDOUT
from eldr.app.codes import AppStatusOkay
from eldr.app.errors import AppRunExecutableError


class AppRunExecutableMixin(object):

    def __init__(self, *args, **kwargs):

        super(AppRunExecutableMixin, self).__init__(*args, **kwargs)

        self._executable_status = AppStatusOkay


    @property
    def executable_status(self):
        """
        Return the current executable exit status value.
        """
        return self._executable_status


    def run_executable(self, cmd, **kwargs):
        """
        Run the specified command.
        """

        # Reset the exit status.
        self._executable_status = AppStatusOkay

        # Set a default list of expected exit status values.
        expected_values = [AppStatusOkay]

        # Store the last few lines of output in case we need to log an error.
        output = collections.deque(maxlen=10)

        # If there is a kwarg called "expected_values", extract it.
        if "expected_values" in kwargs:
            expected_values = kwargs["expected_values"]
            del(kwargs["expected_values"])

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
        if self._executable_status not in expected_values:

            self.log.error("Executable returned unexpected exit status:")
            self.log.error("- command: %s" % " ".join(cmd))
            self.log.error("- exit status: %d" % self._executable_status)
            self.log.error("- output:")

            for line in output:
                self.log.error("> %s" % line)

            raise AppRunExecutableError
