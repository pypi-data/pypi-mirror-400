import json
import shlex

from base_objects import VMEndpoint

from firewheel.control.experiment_graph import require_class


@require_class(VMEndpoint)
class PythonVM:
    """
    This decorator enables a host of functionality to install various Python
    packages onto a VM.
    """

    def __init__(self):
        """Initialize the installed python version (if any)."""
        self.python_version_installed = {}

    def _install_pip(self, python_version="python"):
        """
        Install a version of pip at time -1000.

        Arguments:
            python_version (str): Python executable to use e.g. ``python`` for default,
                ``python3``, ``python3.5`` etc..

        Raises:
            NotImplementedError: If the OS is not supported by this MC (e.g. not linux)
        """
        determined_os = ""
        for dec in self.decorators:
            if "linux" in dec.__name__.lower():
                determined_os = "linux"
                break

        if determined_os == "linux":
            pass
        elif determined_os == "windows":
            raise NotImplementedError
        else:
            raise NotImplementedError
        if (
            python_version not in self.python_version_installed
            or not self.python_version_installed[python_version]
        ):
            pip_install_sched_entry = self.run_executable(
                -1000, python_version, "get-pip.py *.whl", vm_resource=False
            )
            elems = [
                "get-pip.py",
                "setuptools-65.5.1-py3-none-any.whl",
                "wheel-0.32.2-py2.py3-none-any.whl",
                "pip-22.2.2-py3-none-any.whl",
            ]
            for elem in elems:
                pip_install_sched_entry.add_file(elem, elem)
            self.python_version_installed[python_version] = True

    def install_python(self, python_version="3.7", compiled=False):
        """
        Install a newer version of Python on a VM at time -1001.

        Arguments:
            python_version (str): Python minor version to use e.g. ``3.7`` for default.
            compiled (bool): Whether to use the compiled version or pre-built packages.

        Raises:
            NotImplementedError: If the OS or Python version is not supported by this MC.
        """
        determined_os = ""
        for dec in self.decorators:
            if "ubuntu1604" in dec.__name__.lower():
                determined_os = "xenial"
            if "ubuntu1804" in dec.__name__.lower():
                determined_os = "bionic"
            if "ubuntu2204" in dec.__name__.lower():
                determined_os = "jammy"
            if "windows" in dec.__name__.lower():
                determined_os = "windows"
            if determined_os:
                break

        supported_oses = {"xenial", "jammy"}
        supported_python_versions = {"3.7", "3.10"}
        if determined_os not in supported_oses:
            raise NotImplementedError(
                f"Currently only support {', '.join(supported_oses)} images."
            )
        if python_version not in supported_python_versions:
            raise NotImplementedError(
                f"Currently only support Python versions {', '.join(supported_python_versions)}"
            )

        if determined_os == "xenial" and python_version == "3.7":
            if not compiled:
                self.install_debs(-1001, "xenial_python_3.7.tgz")
            else:
                self.drop_file(
                    -1002,
                    "/home/ubuntu/xenial_python3.7_lib.tgz",
                    "xenial_python3.7_lib.tgz",
                )
                self.drop_file(
                    -1002,
                    "/home/ubuntu/xenial_python3.7_bin.tgz",
                    "xenial_python3.7_bin.tgz",
                )
                self.drop_file(
                    -1002,
                    "/home/ubuntu/xenial_python3.7_include.tgz",
                    "xenial_python3.7_include.tgz",
                )
                self.run_executable(
                    -1001,
                    "/bin/tar",
                    arguments=[
                        "-C /usr/local/lib/",
                        "-xvzf",
                        "/home/ubuntu/xenial_python3.7_lib.tgz",
                    ],
                    vm_resource=False,
                )
                self.run_executable(
                    -1001,
                    "/bin/tar",
                    arguments=[
                        "-C /usr/local/bin/",
                        "-xvzf",
                        "/home/ubuntu/xenial_python3.7_bin.tgz",
                    ],
                    vm_resource=False,
                )
                self.run_executable(
                    -1001,
                    "/bin/tar",
                    arguments=[
                        "-C /usr/local/include/",
                        "-xvzf",
                        "/home/ubuntu/xenial_python3.7_include.tgz",
                    ],
                    vm_resource=False,
                )
            self.python_version_installed[python_version] = True
        elif determined_os == "jammy" and python_version == "3.10":
            # Python3.10 comes preinstalled on Jammy, so no need to do anything
            pass
        else:
            raise NotImplementedError(
                f"No support for installing {python_version} on {determined_os}"
            )

    def install_from_source(self, rel_time, paths, python_version="python"):
        """
        Install a list python packages from source. It expects to find a path to
        the source code for the various packages. That is, if you want
        to install the requests package from source. Your input arguments would look
        similar to:

        >>> self.install_from_source(-90, "/home/ubuntu/requests")

        Then on the system, the folder ``/home/ubuntu/requests`` should contain the
        requests source code.

        Args:
            rel_time (int): Relative time at which to run the installation.
                Must be greater than -1000.
            paths (list): List of folder names for the package being installed.
            python_version (str): python executable to use e.g. python for default, python3, etc.
        """
        self._install_pip(python_version)
        if isinstance(paths, str):
            paths = [paths]

        # Need to change dir, then install
        for path in paths:
            self.run_executable(
                rel_time, "cd", arguments=f"{path}; {python_version} setup.py install"
            )

    def install_pip_package_list(
        self, rel_time, package_names, pip_args=None, python_version="python"
    ):
        """
        Install a list of pip package vm_resources.
        This installer uses the OS independent run_executable schedule entry and should be
        preferred over the ``install_pip_package.py`` VMR for portability and facilitate reuse
        of VMRs across model components.

        Arguments:
            rel_time (int): Relative time to run the pip installation at.
                Must be greater than -1000.
            package_names (list): List of pip package VM resources
                (e.g. ``.tgz``, ``.whl``, etc.).
            pip_args (list): List of arguments that will be passed to pip
                when installing the given packages.
            python_version (str): Python executable to use e.g. ``python`` for default,
                ``python3``, ``python3.5`` etc..
        """
        self._install_pip(python_version)
        pip_args = pip_args if pip_args else []
        if isinstance(package_names, str):
            package_names = package_names.split()
        pip_install_sched_entry = self.run_executable(
            rel_time,
            python_version,
            f"-m pip install {shlex.join(pip_args + package_names)}",
        )
        for package in package_names:
            pip_install_sched_entry.add_file(package, package)

    def install_pip_package(
        self, rel_time, package_bundle_name, pip_name, python_version="python"
    ):
        """
        Install a pip package (``.tgz``, ``.whl``, etc.), referenced by name.
        This installer uses the legacy ``install_pip_package.py`` vm_resource from firewheel 1
        and expects a tarball of pip_packages to install. The install_pip_package_list
        installer uses the FIREWHEEL 2 schedule entry and should be preferred over this.

        Arguments:
            rel_time (int): Relative time to run the pip installation at.
                Must be greater than -1000.
            package_bundle_name (str):  Tar file containing 1 or more pip
                packages (``.tgz``, ``.whl``, etc.)
            pip_name (list): List of the pip package(s) to install.
            python_version (str): Python executable to use e.g. ``python`` for default,
                ``python3``, ``python3.5`` etc..
        """

        self._install_pip(python_version)

        if isinstance(pip_name, str):
            pip_name = [pip_name]

        determined_os = ""
        for dec in self.decorators:
            if "linux" in dec.__name__.lower():
                determined_os = "linux"
                break

        if determined_os == "linux":
            self._install_linux(rel_time, package_bundle_name, pip_name, python_version)
        elif determined_os == "windows":
            self._install_windows(
                rel_time, package_bundle_name, pip_name, python_version
            )

    def _install_linux(
        self, rel_time, package_bundle_name, pip_name, python_version="python"
    ):
        dynamic_contents = {"packages": pip_name, "python_version": python_version}
        self.add_vm_resource(
            rel_time,
            "install_pip_package.py",
            dynamic_arg=json.dumps(dynamic_contents),
            static_arg=package_bundle_name,
        )

    def _install_windows(
        self, rel_time, package_bundle_name, pip_name, python_version="python"
    ):
        raise NotImplementedError

    def add_ipython(self, rel_time, python_version="python3"):
        """
        Install the `iPython <https://ipython.org>`_ package.

        Arguments:
            rel_time (int): Relative time to run the pip installation at.
                Must be greater than -1000.
            python_version (str): Python executable to use. Default is ``python3``.
        """
        packages = [
            "matplotlib_inline-0.1.6-py3-none-any.whl",
            "wcwidth-0.2.5-py2.py3-none-any.whl",
            "executing-1.2.0-py2.py3-none-any.whl",
            "ipython-8.8.0-py3-none-any.whl",
            "pexpect-4.8.0-py2.py3-none-any.whl",
            "decorator-5.1.1-py3-none-any.whl",
            "pickleshare-0.7.5-py2.py3-none-any.whl",
            "asttokens-2.2.1-py2.py3-none-any.whl",
            "six-1.16.0-py2.py3-none-any.whl",
            "prompt_toolkit-3.0.36-py3-none-any.whl",
            "backcall-0.2.0-py2.py3-none-any.whl",
            "parso-0.8.3-py2.py3-none-any.whl",
            "jedi-0.18.2-py2.py3-none-any.whl",
            "ptyprocess-0.7.0-py2.py3-none-any.whl",
            "traitlets-5.8.0-py3-none-any.whl",
            "Pygments-2.14.0-py3-none-any.whl",
            "pure_eval-0.2.2-py3-none-any.whl",
            "stack_data-0.6.2-py3-none-any.whl",
        ]
        self.install_pip_package_list(rel_time, packages, python_version=python_version)
