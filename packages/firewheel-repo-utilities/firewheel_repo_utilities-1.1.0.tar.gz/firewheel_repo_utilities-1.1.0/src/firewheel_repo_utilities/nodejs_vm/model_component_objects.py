"""
This module contains all necessary MC Objects for ``utilities.nodejs``.
"""

from pathlib import Path

from linux.ubuntu import UbuntuHost

from firewheel.control.experiment_graph import require_class


@require_class(UbuntuHost)
class NodeJSVM:
    """
    A decorator enabling Node.js functionality on a VM.
    """

    _local_bin_dir = Path("/usr/local/bin")

    def __init__(self, node_version="18.13.0", symlink=False, offline_npm=True):
        """
        Initialize and install Node.js on a VM.

        Issues the commands to install Node.js on a virtual machine with
        the given configuration. The Node.js binaries may be directly
        installed in the VM's ``/usr/local/bin`` directory, or dropped
        elsewhere and symlinked. By default, the VM attempts to set the
        active npm to operate in offline mode.

        Args:
            node_version (str, None): The version of Node.js to install
                on the VM. This must be a valid identifier in the form
                "Major.minor.patch" (e.g., 18.13.0) and correspond to an
                available VM resource compatible with this Ubuntu VM. If
                set to :py:data:`None`, Node will not be installed and
                the assumption will be made that Node already exists on
                the virtual machine.
            symlink (bool): A flag indicating whether to symbolically
                link the Node.js implementation or install it directly
                into the ``/usr/local/bin`` directory. This argument is
                ignored if ``node_version`` is :py:data:`None`.
            offline_npm (bool): A flag indicating whether to configure
                npm to run in offline mode. Since VMs in FIREWHEEL
                experiments typically have no internet access, this
                defaults to :py:data:`True`.
        """
        self.node_version = node_version
        self.node_specifier = f"node-v{self.node_version}-linux-x64"
        self.node_archive = f"{self.node_specifier}.tar.xz"
        self.node_bin = None
        self.node_lib = None
        self.bash_node_prefix = None
        if self.node_version:
            self._install_node(symlink)
        if offline_npm:
            self._set_offline_npm()

    def _install_node(self, symlink):
        # Install Node.js on the VM.
        if symlink:
            self._install_node_symlinked(Path("/opt"))
        else:
            self._install_node_path_update()

    def _install_node_path_update(self):
        # Install Node by extracting the archive and updating paths
        self.node_bin = self._local_bin_dir / self.node_specifier / "bin"
        self.node_lib = self._local_bin_dir / self.node_specifier / "lib/node_modules"
        self._unpack_node(self._local_bin_dir)
        profiles = (
            "/root/.profile /home/ubuntu/.profile /root/.bashrc /home/ubuntu/.bashrc"
        )
        self.run_executable(
            -64,
            "bash",
            arguments=(
                f'-c \'echo "export PATH=$PATH:{self.node_bin}" | tee -a {profiles}&& '
                f'echo "export NODE_PATH={self.node_lib}" | tee -a {profiles}\' '
            ),
            vm_resource=False,
        )
        self.bash_node_prefix = f"PATH=$PATH:{self.node_bin} NODE_PATH={self.node_lib}"

    def _install_node_symlinked(self, node_dir):
        # Install Node by extracting the archive and adding symbolic links
        self._unpack_node(node_dir)
        node_bin_dir = node_dir / self.node_specifier / "bin"
        for exe in ("node", "npm", "npx"):
            exe_path = node_bin_dir / exe
            link_path = self._local_bin_dir / exe
            self.run_executable(-99, "ln", f"-sf {exe_path} {link_path}")

    def _unpack_node(self, extract_dir):
        # Extract and unpack the Node.js archive on the VM
        self.unpack_tar(
            -100,
            self.node_archive,
            options="-xf",
            directory=extract_dir,
            vm_resource=True,
        )

    def _set_offline_npm(self):
        # Set npm to run in offline mode
        self.run_executable(-50, "npm", arguments=["config", "offline", "true"])
