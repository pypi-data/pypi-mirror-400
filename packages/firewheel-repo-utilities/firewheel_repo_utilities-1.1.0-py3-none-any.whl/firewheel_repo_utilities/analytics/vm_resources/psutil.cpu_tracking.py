import sys
import json
import logging
import datetime
import platform
from time import sleep

import psutil
from pythonjsonlogger.json import JsonFormatter


class CPUTracking:
    """Track the system CPU usage using psutil."""

    def __init__(self, refresh_interval_sec):
        """Set up the logging system and take in the refresh rate.

        Args:
            refresh_interval_sec (int): Interval between tracking the statistics.
        """
        self.refresh_interval_sec = refresh_interval_sec
        self._log = logging.getLogger("cpu_tracking")
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

    def run(self):
        """Start tracking the system CPU."""
        self._log.debug("Starting cpu_tracking")

        with open("/opt/analytics/cpu_tracking.log", "a", encoding="utf-8") as outfile:
            # Run every <interval> seconds to get memory statistic
            while True:
                cpu_percents = psutil.cpu_percent(
                    percpu=True
                )  # List of named tuples with stats

                cpu_dict = {
                    "date": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
                }

                for cpu, cpu_percent in enumerate(cpu_percents):
                    cpu_dict["cpu{}".format(cpu)] = cpu_percent

                outfile.write("{}\n".format(json.dumps(cpu_dict)))
                outfile.flush()

                sleep(self.refresh_interval_sec)


if __name__ == "__main__":
    cpu_tracking = CPUTracking(int(sys.argv[1]))
    cpu_tracking.run()
