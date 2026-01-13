#!/usr/bin/env python3
import sys
import pickle
import logging
import platform
from time import sleep
from subprocess import check_output

from pythonjsonlogger.json import JsonFormatter


# pylint: disable=consider-using-f-string
class PortTracking:
    """
    This VMR runs the ``netstat`` command on Linux to track ports opening / closing.
    It runs a default set of options that can be overwritten by passing in file contining
    a pickled dictionary of options.

    The dictionary that is expected is as follows::

        {
            'interval': <optional integer to specify how frequently ports are checked.
                Default 1 second.>,
            'options': <optional string or list of options to overwrite the default ones.
                i.e. '' or []>
        }

    default execution is: ``netstat -t -u -l -p -n``
    """

    def __init__(self, options_filename):
        """Set up the logger and the various netstat options.

        Args:
            options_filename (str): A path to a file which contains the expected parameters.
        """
        self.options_filename = options_filename
        self._log = logging.getLogger("port_tracking")
        self._log.setLevel(logging.DEBUG)
        formatter = JsonFormatter(
            "%(pathname)s %(module)s %(lineno)d %(name)s %(asctime)s %(message)s %(name)s %(levelname)s",
            static_fields={"hostname": platform.node()},
        )

        # Add logging to a file
        file_handler = logging.FileHandler("/opt/analytics/port_tracking.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self._log.addHandler(file_handler)

    def run(self):
        """Run netstat on the given host and log the output."""
        full_command = ["netstat"]

        options = None
        if self.options_filename is not None:
            # There exists an options file. Either load it or fail
            try:
                with open(self.options_filename, "rb") as fhand:
                    options = pickle.load(fhand)
            except (OSError, pickle.UnpicklingError):
                self._log.exception("Error occurred when loading options pickle.")

            if not options:
                self._log.error(
                    "Unable to get netstat options from %s", self.options_filename
                )
                return

        if options is None:
            # No options file was passed in, assume default options are to be used
            options = {}

        full_command += "-t -u -l -p -n".split()

        interval = options.get("interval", 1)

        self._log.debug("Netstat to execute: '%s'", " ".join(full_command))

        # First run to get the Header information and initial open ports
        process_output_lines = check_output(full_command).decode().strip().split("\n")
        self._log.debug("%s\n", process_output_lines[0])
        self._log.debug("%s\n", process_output_lines[1])
        for line in process_output_lines[2:]:
            self._log.debug("INITIAL: %s\n", line)
        old_ports = set(process_output_lines[2:])

        # Now run every <interval> seconds to get changes
        while True:
            sleep(interval)
            process_output = check_output(full_command).decode().strip().split("\n")
            new_ports = set(process_output[2:])

            for port in old_ports - new_ports:
                self._log.debug("DELETED: %s\n", port)
            for port in new_ports - old_ports:
                self._log.debug("ADDED:   %s\n", port)

            old_ports = new_ports


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "None":
        netstat = PortTracking(sys.argv[1])
    else:
        netstat = PortTracking(None)
    netstat.run()
