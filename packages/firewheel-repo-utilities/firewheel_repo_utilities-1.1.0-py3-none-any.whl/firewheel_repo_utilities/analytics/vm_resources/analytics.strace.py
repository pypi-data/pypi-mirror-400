#!/usr/bin/env python3
import os
import sys
import pickle
import logging
import platform
import threading
from time import sleep
from queue import Queue
from subprocess import PIPE, Popen, CalledProcessError, check_output

from pythonjsonlogger.json import JsonFormatter


class Strace:
    """
    This agent runs the strace command on linux to trace the specified command.
    The options for strace are also user specified by passing in file contining
    a pickled dictionary of options.

    The dictionary that is expected is as follows:

    {
        'process': <process name to be traced by strace>,
        'first_match_only': <boolean on whether pgrep should continue trying to match processes>,
        'output_dir': <directory where all strace output files will be stored
            (i.e. sets the ``-o`` option)>
        'options': <optional string or list of options to overwrite the default ones
            (except for ``-p`` and ``-o``). i.e. ``'-f -e trace=network,process,file'``
            or   ``['-f', '-e', 'trace=network,process,file']``>,
    }
    default execution is:
        ``strace -ff -tt -s 1024 -o <output_dir>/<matched process's command>.trace
            -p <pid of matched process>``

    """

    def __init__(self, options_filename):
        """Set up the logger and the various strace options

        Args:
            options_filename (str): A path to a file which contains the expected parameters.
        """
        self.options_filename = options_filename
        self._log = logging.getLogger("strace")
        self._log.setLevel(logging.DEBUG)
        formatter = JsonFormatter(
            "%(pathname)s %(module)s %(lineno)d %(name)s %(asctime)s %(message)s %(name)s %(levelname)s",
            static_fields={"hostname": platform.node()},
        )

        # Add logging to stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self._log.addHandler(console_handler)

        self.running_straces = (
            Queue()
        )  # This is a queue because a thread adds to it and queues are synchronous
        self.first_match_only = True

        # Use strace_command to build up the final strace command to be executed
        self.strace_command = ["strace"]
        self.process_regex = None
        self.output_dir = None
        self.options = None
        self.stop_pgrep = False

    def _assign_parameters(self):
        """Extracts the parameters from the ``options_filename``.

        Returns:
            bool: True if all required options were provided, False otherwise.
        """
        strace_args = None
        try:
            with open(self.options_filename, "rb") as fhand:
                strace_args = pickle.load(fhand)
        except (OSError, pickle.UnpicklingError):
            self._log.exception(
                "An error occurred when unpickling %s", self.options_filename
            )

        # Exit if the data file didn't exist or wasn't valid
        if not strace_args:
            self._log.error(
                "Unable to get strace options from %s", self.options_filename
            )
            return False

        required_args = ["process_regex", "first_match_only", "output_dir"]
        missing_args = [ra for ra in required_args if ra not in strace_args]
        if missing_args:
            self._log.error(
                "Missing the following required arguments: %s", missing_args
            )
            return False

        self.process_regex = strace_args["process_regex"]
        self.first_match_only = strace_args["first_match_only"]
        self.output_dir = strace_args["output_dir"]

        # Use user supplied options if they exist, otherwise use the default options
        if "options" in strace_args:
            if isinstance(strace_args["options"], list):
                self.options = strace_args["options"]
            else:
                self.options = strace_args["options"].split()
        else:
            self.options = "-ff -tt -s 1024".split()

        return True

    def run(self):
        """Runs the ``strace`` command with the provided paremeters."""
        if not self._assign_parameters():
            return

        self.strace_command += self.options

        pgrep_thread = threading.Thread(target=self._check_pgrep)
        pgrep_thread.start()

        # Block until the pgrep thread has found a match and created a process
        while self.running_straces.empty():
            sleep(5)

        # Only exit when the queue has been emptied and we only were wanting the first match.
        # Otherwise keep running
        while not (self.running_straces.empty() and self.first_match_only):
            # Check each process to see if it's still running
            still_running_straces = []
            while not self.running_straces.empty():
                running_strace = self.running_straces.get()

                if running_strace.poll() is not None:
                    # It's actually a terminated_strace. Get and log the output
                    stdout_data, stderr_data = running_strace.communicate()
                    if stdout_data:
                        self._log.debug(
                            "Executed strace output",
                            {
                                "fd": "stdout",
                                "pid": running_strace.pid,
                                "msg": stdout_data,
                            },
                        )
                    if stderr_data:
                        self._log.debug(
                            "Executed strace output",
                            {
                                "fd": "stderr",
                                "pid": running_strace.pid,
                                "msg": stderr_data,
                            },
                        )
                else:
                    still_running_straces.append(running_strace)

            # Put them all back into the queue
            for still_running in still_running_straces:
                self.running_straces.put(still_running)

            sleep(30)

    def _check_pgrep(self):
        """Identify a process using ``pgrep``."""
        # pgrep for a process until a match
        already_matched = {}  # {pid: ['<process>', ...], ...}
        exclude_filters = ["strace", "tail"]
        previous_pgrep = None
        self.stop_pgrep = False
        while not self.stop_pgrep:
            try:
                raw_output = check_output(
                    ["pgrep", "-l", "-f", "{}".format(self.process_regex)]
                ).decode()
                self._log.debug("raw_output: '%s'", raw_output)
            except CalledProcessError:
                self._log.debug(
                    "pgrep found no matching processes for regex '%s'",
                    self.process_regex,
                )
                sleep(1)
                continue

            if raw_output != previous_pgrep:
                # pgrep returned something new, process it.
                previous_pgrep = raw_output

                matches = {}
                for output_line in raw_output.strip().split("\n"):
                    # Check if this returned processes should be filtered out
                    for exclude_filter in exclude_filters:
                        if exclude_filter in output_line:
                            break
                    else:
                        split_output_line = output_line.split()
                        pid, matched_full_command = (
                            split_output_line[0],
                            " ".join(split_output_line[1:]),
                        )
                        matches[pid] = matched_full_command

                if matches:
                    self._log.debug(matches)

                    # Execute the matches
                    for pid, matched_full_command in matches.items():
                        if (
                            pid in already_matched
                            and matched_full_command in already_matched[pid]
                        ):
                            continue

                        already_matched[pid] = already_matched.get(pid, []).append(
                            matched_full_command
                        )
                        self._execute_strace(pid, matched_full_command)

                        with open(
                            os.path.join(self.output_dir, "command_info.log"),
                            "a",
                            encoding="utf-8",
                        ) as info_log:
                            info_log.write("{},{}\n".format(pid, matched_full_command))

                    if self.first_match_only:
                        self.stop_pgrep = True

            sleep(1)

    def _execute_strace(self, pid, matched_full_command):
        """Run the ``strace`` command on the given PID.

        Args:
            pid (int): The process ID to trace
            matched_full_command (str): The command of the to-be-traced process.
        """
        env = os.environ.copy()
        env["TZ"] = "UTC"

        # Create the output location if necessary
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        output_filename = "{}.trace".format(
            os.path.basename(matched_full_command.split()[0])
        )

        current_strace_command = list(self.strace_command)
        current_strace_command += ["-o", os.path.join(self.output_dir, output_filename)]
        current_strace_command += ["-p", str(pid)]

        self._log.debug("Strace to execute: '%s'", " ".join(current_strace_command))
        # pylint: disable=consider-using-with
        running_process = Popen(
            current_strace_command, stdout=PIPE, stderr=PIPE, env=env
        )
        self.running_straces.put(running_process)


if __name__ == "__main__":
    strace = Strace(sys.argv[1])
    strace.run()
