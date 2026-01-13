import sys
import logging
import platform
from time import sleep

import psutil
from pythonjsonlogger.json import JsonFormatter


class SystemMemoryTracking:
    """Track the system memory using psutil."""

    def __init__(self, refresh_interval_sec):
        """Set up the logging system and take in the refresh rate.

        Args:
            refresh_interval_sec (int): Interval between tracking the statistics.
        """
        self.refresh_interval_sec = refresh_interval_sec
        self._log = logging.getLogger("system_memory_tracking")
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

        # Add logging to a file
        file_handler = logging.FileHandler("/opt/analytics/system_memory_tracking.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self._log.addHandler(file_handler)

    def run(self):
        """Start tracking the system memory."""
        self._log.debug("Starting system_memory_tracking")

        # Run every <interval> seconds to get memory statistic
        while True:
            mem = psutil.virtual_memory()  # Named tuple with stats

            mem_dict = {
                "analytics.system_memory_tracking.{}".format(k): v
                for k, v in mem._asdict().items()
            }
            self._log.debug(mem_dict)

            sleep(self.refresh_interval_sec)


if __name__ == "__main__":
    system_memory_tracking = SystemMemoryTracking(int(sys.argv[1]))
    system_memory_tracking.run()
