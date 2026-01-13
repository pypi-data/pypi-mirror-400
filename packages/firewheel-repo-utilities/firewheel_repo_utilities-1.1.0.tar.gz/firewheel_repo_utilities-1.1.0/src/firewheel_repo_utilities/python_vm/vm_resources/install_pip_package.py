#!/usr/bin/env python3
import os
import sys
import json
import time
import tarfile
from subprocess import PIPE, Popen


# pylint: disable=useless-object-inheritance,consider-using-f-string,unspecified-encoding
class InstallPipPackage(object):
    """
    This vm_resource is based on the install debs vm_resource.

    Arguments:
        dynamic_file (str): This file should contain a json encoded dictionary
            which has a list of packages to install.
        static_file (str): The static file should be a tar file containing
            the pip packages (tgz/whl) that are downloaded when installing the
            target pip package. The static file name MUST have the same name as
            the pip package you are installing.

    Examples:
        Example of creating the static file::

            mkdir /home/ubuntu/ncclient
            sudo pip install --download /home/ubuntu/ncclient ncclient
            tar -czvf ncclient.tgz /home/ubuntu/ncclient

        Example dynamic_file::

            {
                'packages' : [
                                cffi,
                                cryptography,
                                ncclient
                            ]
            }
    """

    def __init__(self, dynamic_file=None, static_file=None):
        """
        Set up the various configurations necessary to install a python package.

        Arguments:
            dynamic_file (str): The path to a configuration file.
            static_file (str): The path to a tarball containing the packages to install.
        """
        # Split on '.' in an attempt to get the name of the static
        # file without extensions. Binary files don't need extensions
        # though so default to just the static_file name
        package_name = os.path.basename(static_file)
        if "." in package_name:
            package_name = os.path.splitext(package_name)[0]

        self.install_dir = "/tmp/%s-agent-install" % package_name
        self.pip_package = package_name

        # don't need to check from /tmp/agents since this vm_resource
        # is currently running there
        if not os.path.exists(self.install_dir):
            os.makedirs(self.install_dir)

        if not static_file or static_file == "None":
            print(
                json.dumps({"install_pip_package": "No static file provided. Exiting"})
            )
            return

        if not dynamic_file or dynamic_file == "None":
            print(
                json.dumps({"install_pip_package": "No dynamic file provided. Exiting"})
            )
            return

        with open(dynamic_file, "r", encoding="utf-8") as fname:
            self.config = json.load(fname)

        self.static_file = static_file

        self.pip_lock = "/tmp/pip-lock"

    def run(self):
        """
        Perform all the major work of installing 1 or more Python packages.

        Raises:
            OSError: If the tarfile is in an invalid format.
        """
        # untar the static files
        with tarfile.open(self.static_file) as tar:
            tar.extractall(path=self.install_dir)

        # Verify our extract and get the directory name with actual pip files.
        untared_contents = os.listdir(self.install_dir)
        if len(untared_contents) != 1 or not os.path.isdir(
            os.path.join(self.install_dir, untared_contents[0])
        ):
            raise OSError("Invalid tarfile format: Need exactly 1 directory.")

        # Acquire a file-system lock for running pip
        while True:
            try:
                os.mkdir(self.pip_lock)
                break
            except OSError:
                time.sleep(1)

        # now that we have the files to install, install them
        static_dir = os.path.join(self.install_dir, untared_contents[0])
        if self.config.get("python_version"):
            python_version = self.config["python_version"]
        else:
            python_version = "python"
        for package in self.config["packages"]:
            # pylint: disable=consider-using-with
            install = Popen(
                [
                    python_version,
                    "-m",
                    "pip",
                    "install",
                    "--no-index",
                    "--find-links=%s" % static_dir,
                    package,
                ],
                stdout=PIPE,
                stderr=PIPE,
            )

            output = install.communicate()
            if install.returncode != 0:
                # Output is a tuple (<stdout>, <stderr>)
                print(output[1])

            print(
                json.dumps(
                    {
                        "vm_resource": "InstallPipPackage",
                        "status": "success",
                        "message": "Installed package %s" % package,
                    }
                )
            )

        # Release the file-system pip lock
        os.rmdir(self.pip_lock)


if __name__ == "__main__":
    install_pkg = InstallPipPackage(sys.argv[1], sys.argv[2])
    install_pkg.run()
