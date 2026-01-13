import sys
import logging
import platform
from time import sleep

import psutil
from pythonjsonlogger.json import JsonFormatter


class DiskUsageTracking:
    """Track the VM's disk usage using psutil."""

    def __init__(self, refresh_interval_sec):
        """Set up the logging system and take in the refresh rate.

        Args:
            refresh_interval_sec (int): Interval between tracking the statistics.
        """
        self.refresh_interval_sec = refresh_interval_sec
        self._log = logging.getLogger("disk_usage_tracking")
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
        file_handler = logging.FileHandler("/opt/analytics/disk_usage_tracking.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self._log.addHandler(file_handler)

    def run(self):
        """Start tracking the system disk usage."""
        self._log.debug("Starting disk_usage_tracking")

        disk_partitions = psutil.disk_partitions(all=False)

        # Run every <interval> seconds to get memory statistic
        while True:
            # Get the usage statistics for each disk partition
            disk_usages = {}
            for partition in disk_partitions:
                disk_usage = psutil.disk_usage(
                    partition.mountpoint
                )  # Named tuple with stats
                disk_usages[
                    "analytics.disk_usage_tracking.{}".format(partition.mountpoint)
                ] = disk_usage._asdict()
            self._log.debug(disk_usages)

            sleep(self.refresh_interval_sec)


if __name__ == "__main__":
    disk_usage_tracking = DiskUsageTracking(int(sys.argv[1]))
    disk_usage_tracking.run()
