import pickle

from base_objects import VMEndpoint
from utilities.tools import Utilities
from utilities.python import PythonVM

from firewheel.control.experiment_graph import require_class


# pylint: disable=protected-access
def run_once_with_unique(unique_args, unique_kwargs):
    """
    Runs the function only if the combined specified args and kwargs are unique to the execution.

    Args:
        unique_args (list): List of integers of positions
        unique_kwargs (list): List of strings of kwargs

    Returns:
        function: The decorated function.
    """

    def real_decorator(func):
        """The decorator which takes in the function.

        Args:
            func (function): The function to check.

        Returns:
            function: The wrapped function or None if it was previously executed.
        """

        def wrapper(*args, **kwargs):
            """Ensures the arguments are unique and that the function hasn't been
            executed previously. Then it returns the function.

            Arguments:
                *args (list): A list of arguments to the function.
                **kwargs (dict): A list of keyword arguments to the function.

            Returns:
                function: The wrapped function or None if it was previously executed.
            """
            # Private dict that keeps track of the different executions
            if "_ran_funcs" not in args[0].__dict__:
                args[0]._ran_funcs = {}

            if func.__name__ in args[0]._ran_funcs:
                # Determine if this execution is different from a prior execution
                already_ran = True
                for execution in args[0]._ran_funcs[func.__name__]:
                    exc_is_different = False
                    for pos in unique_args:
                        if args[pos] != execution[pos]:
                            exc_is_different = True
                            break
                    else:
                        for key in unique_kwargs:
                            if kwargs[key] != execution[key]:
                                exc_is_different = True
                                break

                    if not exc_is_different:
                        break
                else:
                    already_ran = False

            else:
                args[0]._ran_funcs[func.__name__] = []
                already_ran = False

            if not already_ran:
                new_execution = {pos: args[pos] for pos in unique_args}
                new_execution.update({k: kwargs[k] for k in unique_kwargs})
                args[0]._ran_funcs[func.__name__].append(new_execution)
                return func(*args, **kwargs)

            return None

        wrapper.__doc__ = func.__doc__
        return wrapper

    return real_decorator


# pylint: disable=protected-access
def run_once(func):
    """
    Each function decorated with this can only be ran once in each object calling it.

    Arguments:
        func (function): The passed in function to check.

    Returns:
        function: The wrapped function or None if it was previously executed.
    """

    def wrapper(*args, **kwargs):
        """Ensures the function hasn't been executed before.

        Arguments:
            *args (list): A list of arguments to the function.
            **kwargs (dict): A list of keyword arguments to the function.

        Returns:
            function: The wrapped function or None if it was previously executed.
        """
        if "_ran_funcs" not in args[0].__dict__:
            args[0]._ran_funcs = {}
        if func.__name__ not in args[0]._ran_funcs:
            args[0]._ran_funcs[func.__name__] = True
            return func(*args, **kwargs)
        return None

    wrapper.__doc__ = func.__doc__
    return wrapper


@require_class(VMEndpoint)
@require_class(Utilities)
@require_class(PythonVM)
class Analytics:
    """
    This class provides numerous methods available for any decorated Vertex.
    By default, this class performs the following operations:

    * Installs the JSON logger python package.
    * Creates an ``/opt/analytics`` directory on the VM.
    * Adds the ``kill_analytics.py`` VM resource to the VM.

    All other analytic functions must be called individually.
    """

    def __init__(self, python_version="python3.10"):
        """
        Install/configure a few VMRs which are required by all analytic methods.

        Arguments:
            python_version (str): The version of python that will be used for analytics
        """
        self.python_version = python_version

        self.install_pip_package_list(
            -100,
            ["python_json_logger-4.0.0-py3-none-any.whl"],
            python_version=self.python_version,
        )
        self.run_executable(-101, "mkdir", "/opt/analytics", vm_resource=False)
        self.drop_file(
            -100,
            "/opt/analytics/kill_analytics.py",
            "kill_analytics.py",
            executable=True,
        )

    def strace(
        self,
        time,
        process_regex,
        options=None,
        first_match_only=True,
        tailf_traces=True,
    ):
        """
        Adds a VM resource to call `pgrep <https://linux.die.net/man/1/pgrep>`_
        for the passed in regular expression until a match, then use
        `strace <https://strace.io/>`_ on the matched PIDs.

        Arguments:
            time (int): The time to run the ``strace`` VM resource
            process_regex (str): The regex to match on to find the PIDs to ``strace``
            options (str): Optional arguments with which to override the call to ``strace``.
                Default options are ``-ff -tt -s 1024``
            first_match_only (bool): Whether ``pgrep`` should keep finding matches or
                stop after the first match. Defaults to ``True``.
            tailf_traces (bool): Whether each outputted trace file should use
                :py:meth:`analytics.Analytics.tailf_dir` which causes it to be
                added to logs. Defaults to ``True``.
        """
        if options is None:
            options = "-ff -tt -s 1024"

        if tailf_traces:
            output_dir = f"/opt/analytics/traces/tailf_dirs/{time}"
        else:
            output_dir = f"/opt/analytics/traces/no_tailf_dirs/{time}"

        strace_args = pickle.dumps(
            {
                "process_regex": process_regex,
                "options": options,
                "first_match_only": first_match_only,
                "output_dir": output_dir,
            },
            protocol=0,
        ).decode()

        self.add_vm_resource(time, "analytics.strace.py", strace_args, None)

        if tailf_traces:
            self.tailf_dir(max(1, time - 1), output_dir, "trace\\\\.[0-9]+")

    @run_once_with_unique([2], [])  # Only add tailf_dir to any directory once
    def tailf_dir(self, time, directory, matching_regex):
        r"""
        Will run ``tail -f`` on any **NEW** file in the specified directory with filename
        matching the supplied regex.

        Note:
            This method is decorated with the :py:func:`analytics.run_once_with_unique` decorator
            which ensures that, even if the method is called multiple times, the code will
            only be executed once per unique directory provided. That is, users won't accidentally
            be able to schedule multiple instances of ``tail -f`` on the same directory (as that
            would provide redundant data).

        Arguments:
            time (int): Positive integer of when tracking will be scheduled.
            directory (str): Directory to track. It will be created if it doesn't exist
            matching_regex (str): Very simple regex to match against filenames, double escaped.
                e.g. ``\\.\\*\\\\.log`` will match all files that end with ``.log``.
        """
        assert time >= 1
        self.install_inotify()
        self.run_executable(
            time,
            "analytics.tailf_dir.sh",
            f"{directory} {matching_regex}",
            vm_resource=True,
        )

    @run_once
    def install_inotify(self):
        """
        Installs the `inotify-tools <https://github.com/inotify-tools/inotify-tools>`_
        package which helps with file system monitoring. For more information about this package
        see the following article:
        https://medium.com/100-days-of-linux/an-introduction-to-file-system-monitoring-tools-afd99164ce66

        Note:
            This method is decorated with the :py:func:`analytics.run_once` decorator
            which ensures that, even if the method is called multiple times, the code will
            only be executed once.
        """
        self.install_debs(-76, "inotify-tools_3.14-1.tgz")

    @run_once
    def run_tcpdump(self, options=None, install_tcpdump=False):
        """
        Schedule ``tcpdump`` to be called and the output saved to
        ``/opt/analytics/pcaps/tmp.pcap`` on the VM.

        Note:
            This method is decorated with the :py:func:`analytics.run_once` decorator
            which ensures that, even if the method is called multiple times, the code will
            only be executed once.

        Arguments:
            options (str): A string of options that can be used with the ``tcpdump`` command.
                We recommend avoiding setting this unless you are familiar with ``tcpdump``.
                For more information about the options see:
                https://www.tcpdump.org/manpages/tcpdump.1.html.
            install_tcpdump (bool): A boolean value indicating whether or not
                tcpdump should be installed as part of this function call.
        """
        if install_tcpdump:
            self.add_tcpdump()

        if options is None:
            options = "-U -w /opt/analytics/pcaps/tmp.pcap -Z root"

        self.run_executable(-1, "mkdir", "/opt/analytics/pcaps", vm_resource=False)
        self.run_executable(1, "tcpdump", options, vm_resource=False)

    @run_once
    def add_port_tracking(self, refresh_interval_sec=1):
        """Adds a VM resource to repeatedly call `netstat <https://linux.die.net/man/8/netstat>`_
        and track any changes.

        Note:
            This method is decorated with the :py:func:`analytics.run_once` decorator
            which ensures that, even if the method is called multiple times, the code will
            only be executed once.

        Arguments:
            refresh_interval_sec (int): Interval to track the statistics (e.g. time
                between ``netstat`` calls). Defaults to ``1``.
        """
        netstat_args = pickle.dumps(
            {"interval": refresh_interval_sec}, protocol=0
        ).decode()
        self.add_vm_resource(1, "analytics.port_tracking.py", netstat_args, None)

    @run_once
    def add_system_memory_tracking(self, refresh_interval_sec=5):
        """
        Uses `psutil <https://pypi.org/project/psutil/>`__ to track the systems memory
        statistics every ``<interval>`` seconds. Writes to
        ``/opt/analytics/system_memory_tracking.log`` on the VM.

        Note:
            This method is decorated with the :py:func:`analytics.run_once` decorator
            which ensures that, even if the method is called multiple times, the code will
            only be executed once.

        Arguments:
            refresh_interval_sec (int): Interval to track the statistics. Defaults to ``5``.
        """
        self.install_psutil()
        fn = "psutil.system_memory_tracking.py"
        full_path = f"/opt/analytics/{fn}"
        self.drop_file(-50, full_path, fn)
        self.run_executable(
            1,
            self.python_version,
            f"{full_path} {refresh_interval_sec}",
            vm_resource=False,
        )

    @run_once
    def add_disk_usage_tracking(self, refresh_interval_sec=5):
        """
        Uses `psutil <https://pypi.org/project/psutil/>`__ to track the systems disk usage
        on each partition every ``<interval>`` seconds. Writes to
        ``/opt/analytics/disk_usage_tracking.log`` on the VM.

        Note:
            This method is decorated with the :py:func:`analytics.run_once` decorator
            which ensures that, even if the method is called multiple times, the code will
            only be executed once.

        Arguments:
            refresh_interval_sec (int): Interval to track the statistics. Defaults to ``5``.
        """
        self.install_psutil()
        fn = "psutil.disk_usage_tracking.py"
        full_path = f"/opt/analytics/{fn}"
        self.drop_file(-50, full_path, fn)
        self.run_executable(
            1,
            self.python_version,
            f"{full_path} {refresh_interval_sec}",
            vm_resource=False,
        )

    @run_once
    def add_disk_io_tracking(self, refresh_interval_sec=5):
        """
        Uses `psutil <https://pypi.org/project/psutil/>`__ to track the systems disk IO
        statistics on each partition every ``<interval>`` seconds. Writes to
        ``/opt/analytics/disk_io_tracking.log`` on the VM.

        Note:
            This method is decorated with the :py:func:`analytics.run_once` decorator
            which ensures that, even if the method is called multiple times, the code will
            only be executed once.

        Arguments:
            refresh_interval_sec (int): Interval to track the statistics. Defaults to ``5``.
        """
        self.install_psutil()
        fn = "psutil.disk_io_tracking.py"
        full_path = f"/opt/analytics/{fn}"
        self.drop_file(-50, full_path, fn)
        self.run_executable(
            1,
            self.python_version,
            f"{full_path} {refresh_interval_sec}",
            vm_resource=False,
        )

    @run_once
    def add_network_io_tracking(self, refresh_interval_sec=1):
        """
        Uses `psutil <https://pypi.org/project/psutil/>`__ to track the systems network IO
        on each NIC every ``<interval>`` seconds. Writes to
        ``/opt/analytics/network_io_tracking.log`` on the VM.

        Note:
            This method is decorated with the :py:func:`analytics.run_once` decorator
            which ensures that, even if the method is called multiple times, the code will
            only be executed once.

        Arguments:
            refresh_interval_sec (int): Interval to track the statistics. Defaults to ``1``.
        """
        self.install_psutil()
        fn = "psutil.network_io_tracking.py"
        full_path = f"/opt/analytics/{fn}"
        self.drop_file(-50, full_path, fn)
        self.run_executable(
            1,
            self.python_version,
            f"{full_path} {refresh_interval_sec}",
            vm_resource=False,
        )

    @run_once
    def add_cpu_tracking(self, refresh_interval_sec=1):
        """
        Uses `psutil <https://pypi.org/project/psutil/>`__ to track the systems CPU
        frequencies on each CPU every ``<interval>`` seconds. Writes the output to
        ``/opt/analytics/cpu_tracking.log`` on the VM.

        Note:
            This method is decorated with the :py:func:`analytics.run_once` decorator
            which ensures that, even if the method is called multiple times, the code will
            only be executed once.

        Arguments:
            refresh_interval_sec (int): Interval to track the statistics. Defaults to ``1``.
        """
        self.install_psutil()
        fn = "psutil.cpu_tracking.py"
        full_path = f"/opt/analytics/{fn}"
        self.drop_file(-50, full_path, fn)
        self.run_executable(
            1,
            self.python_version,
            f"{full_path} {refresh_interval_sec}",
            vm_resource=False,
        )

    @run_once
    def install_psutil(self):
        """
        Installs `psutil <https://pypi.org/project/psutil/>`__ on the VM.

        Raises:
            NotImplementedError: If the python version is not python3.7 or python3.10

        Note:
            This method is decorated with the :py:func:`analytics.run_once` decorator
            which ensures that, even if the method is called multiple times, the code will
            only be executed once.
        """
        # Pull out the version number, which is the needed argument for installing python
        python_version_num = self.python_version.split("python")[1]

        self.install_python(python_version=python_version_num, compiled=False)

        if self.python_version == "python3.7":
            psutil_package = "psutil-5.9.1-cp37-cp37m-manylinux_2_12_x86_64.manylinux2010_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl"  # noqa: E501
        elif self.python_version == "python3.10":
            psutil_package = "psutil-5.9.8-cp36-abi3-manylinux_2_12_x86_64.manylinux2010_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl"  # noqa: E501
        else:
            raise NotImplementedError(
                "psutil installation only supported for python3.7 and python3.10"
            )

        self.install_pip_package_list(
            -100,
            [psutil_package],
            python_version=self.python_version,
        )
