"""This module contains all necessary Model Component Objects for utilities.tools."""


class Utilities:
    """
    An object which provides various utility functions for VMs.
    """

    def add_wireshark(self):
        """
        Install Wireshark on a VM.
        Currently, only Ubuntu 22.04 is supported.
        """
        determined_os = self.get_and_validate_vm_os({"ubuntu2204"})
        if determined_os == "ubuntu2204":
            self.install_debs(-40, "wireshark-3.6.2.tgz")

    def add_tcpdump(self):
        """Install ``libpcap`` and tcpdump on a VM."""
        self.install_build_tools()

        # Install libpcap
        libpcap_name = "libpcap-1.10.4"
        self.drop_file(-58, f"/tmp/{libpcap_name}.tar.gz", f"{libpcap_name}.tar.gz")  # noqa: S108
        self.run_executable(
            -57, "/bin/tar", f"-C /tmp/ -xzf /tmp/{libpcap_name}.tar.gz"
        )
        self.run_executable(
            -56,
            "/bin/bash",
            f"-c 'cd /tmp/{libpcap_name}; ./configure; make; make install;'",
        )

        # Install tcpdump
        tcpdump_name = "tcpdump-4.99.4"
        self.drop_file(-55, f"/tmp/{tcpdump_name}.tar.gz", f"{tcpdump_name}.tar.gz")  # noqa: S108
        self.run_executable(
            -54, "/bin/tar", f"-C /tmp/ -xzf /tmp/{tcpdump_name}.tar.gz"
        )
        self.run_executable(
            -53,
            "/bin/bash",
            f"-c 'cd /tmp/{tcpdump_name}; ./configure; make; make install;'",
        )

    def add_docker(self):
        """
        Install Docker on a VM.
        Currently, only Ubuntu 22.04 is supported.
        """
        determined_os = self.get_and_validate_vm_os({"ubuntu2204"})
        if determined_os == "ubuntu2204":
            self.install_debs(-40, "docker-jammy-debs.tgz")

    def install_build_tools(self):
        """
        Install several utilities to make building packages easier on Linux.
        This includes make, cmake, flex, gcc, python3-dev, curl, and bison.
        Currently, only Ubuntu 22.04 is supported.
        """
        determined_os = self.get_and_validate_vm_os({"ubuntu2204"})

        if determined_os == "ubuntu2204":
            self.install_debs(-59, "jammy-build-tools.tgz")

    def get_and_validate_vm_os(self, supported_oses=None):
        """
        Get the operating system from a VM and check to see if
        an approved operating system is used.

        Arguments:
            supported_oses (set): A set of supported operating systems.

        Returns:
            str: The matched operating system.

        Raises:
            NotImplementedError: If the VM has an unsupported OS.
        """

        if supported_oses is None:
            supported_oses = set()

        determined_os = ""
        for dec in self.decorators:
            if "ubuntu2204" in dec.__name__.lower():
                determined_os = "ubuntu2204"
            if determined_os:
                break

        if determined_os not in supported_oses:
            raise NotImplementedError(
                f"Currently only support '{supported_oses}' images."
            )

        return determined_os
