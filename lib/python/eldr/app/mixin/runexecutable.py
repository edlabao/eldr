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

        This is a generator and must be used as an iterable in order to work
        correcty.

        :Parameters:
            cmd : List object that contains the executable to run as the first
                element and each additional argument and value as individual
                list elements to make it suitable for passing to the Popen
                  fuction.
            kwargs : Keyword arguments to pass to the Popen function. This also
                accepts the following keyword arguments that are stripped prior
                to passing kwargs to Popen:
                    expected_statuses : List of integer values which are
                    acceptable exit codes for the executable (default=[0])
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
