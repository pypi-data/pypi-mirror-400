.. _utilities.python_mc:

################
utilities.python
################

Provides a MC object representation of Python within the experiment.
This method calls by VM objects such as installing newer versions of Python and adding pip packages.
Additionally, this MC contains copies of several common Python packages which can be installed/used by VMs.

**Model Component Dependencies:**
    * :ref:`base_objects_mc`

.. warning::

    Some required VM resource files are not available on the Internet, though they are unlikely to be used in recent experiments. If you do **NOT** need the following files [`python-pip-1404.tgz`, `python-pip-1604.tgz`, `xenial_python_3.7.tgz`, `xenial_python3.7_bin.tgz`, `xenial_python3.7_include.tgz`, and `xenial_python3.7_lib.tgz`] you should continue to run the MC INSTALL scripts and then manually create ``.utilities.python.installed``. Please contact the FIREWHEEL developers if you need these files or have additional questions.

************
VM Resources
************
* ``python-pip-1404.tgz`` -- Pip (as a debian package) for Python 2 on Ubuntu 14.04.
* ``python-pip-1604.tgz`` -- Pip (as a debian package) for Python 2 on Ubuntu 16.04.
* ``xenial_python3.7_bin.tgz`` -- Python 3.7 binaries compiled for Xenial. Should be placed in ``/usr/local/bin/`` if needed.
* ``xenial_python3.7_lib.tgz`` -- Python 3.7 libraries compiled for Xenial. Should be placed in ``/usr/local/lib/`` if needed.
* ``xenial_python_3.7.tgz`` -- Python 3.7 debian packages for Xenial.
* ``get-pip.py`` -- A bootstrapping script that enables users to install ``pip``, ``setuptools``, and ``wheel`` in Python environments that don't already have them. This will install pip version 18.1. See https://github.com/pypa/get-pip for more details.
* ``install_pip_package.py`` -- A legacy VRM that can install a tarball of Python packages on a Linux system (used by :py:meth:`utilities.python.PythonVM.install_pip_package`).

Pip Packages
============
* ``certifi-2019.3.9-py2.py3-none-any.whl`` - `Certifi <https://certifiio.readthedocs.io/en/latest/>`_ provides Mozilla's carefully curated collection of Root Certificates for validating the trustworthiness of SSL certificates while verifying the identity of TLS hosts.
* ``chardet-3.0.4-py2.py3-none-any.whl`` - `Chardet <https://pypi.org/project/chardet/>`_ is a universal encoding detector for Python 2 and 3.
* ``idna-2.8-py2.py3-none-any.whl`` - `Internationalized Domain Names in Applications (IDNA) <https://pypi.org/project/idna/>`_.
* ``pip-18.1-py2.py3-none-any.whl`` - The PyPA recommended tool for installing Python packages.
* ``requests-2.21.0-py2.py3-none-any.whl`` - `Requests <https://pypi.org/project/requests/>`_ is a simple, yet elegant, HTTP library.
* ``setuptools-40.4.3-py2.py3-none-any.whl`` - `Setuptools <https://pypi.org/project/setuptools/>`_ enables users to easily download, build, install, upgrade, and uninstall Python packages.
* ``urllib3-1.24.2-py2.py3-none-any.whl`` - `urllib3 <https://pypi.org/project/urllib3/>`_ is a powerful, user-friendly HTTP client for Python.
* ``wheel-0.32.2-py2.py3-none-any.whl`` - `wheel <https://pypi.org/project/wheel/>`_ is the reference implementation of the Python wheel packaging standard, as defined in PEP 427.
* ``ipython`` - The `iPython <https://ipython.org>`_ package and all its dependencies.

Upgrading Python
================
To install a newer version of Python in a VM, there are two primary methods:

1. Getting the compiled packages provided by some service (e.g. the `deadsnakes PPA <https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa>`_).
2. Compiling Python on the same image that will be used in the experiments.

This MC supports installing debian packages for:

* Ubuntu 16.04 (i.e. Xenial)
    * Python 3.7

This MC supports installing compiled Python for:

* Ubuntu 16.04 (i.e. Xenial)
    * Python 3.7

VMs can use these available upgraded versions of Python by decorating their VMs with :py:class:`utilities.python.PythonVM` and then calling the :py:meth:`utilities.python.PythonVM.install_python` method.

Creating Compiled Python
========================

To create a new compiled version of Python, users should launch the exact image of their desired OS, then follow the steps below:

1. Download the Python source code.

   .. code-block:: bash

        wget https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz

2. Install necessary dependencies. We recommend following either the `official Python documentation <https://devguide.python.org/setup/#build-dependencies>`_ or the `Real Python guide <https://realpython.com/installing-python/#how-to-build-python-from-source-code>`_.

3. Build Python.

    .. code-block:: bash

        tar xzvf Python-3.7.12.tgz
        cd Python-3.7.12
        ./configure --enable-optimizations --enable-shared --prefix=/usr/local --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"

    .. note::

        You may want other and/or different flags for your version of Python.

4. Install it

    .. code-block:: bash

        make altinstall

5. Package up the installed version of Python

    .. code-block:: bash

        cd /usr/local/include
        tar -czvf xenial_python3.7_include.tgz python3.7m/
        mv xenial_python3.7_include.tgz /home/ubuntu
        cd /usr/local/bin
        tar -czvf xenial_python3.7_bin.tgz *
        mv xenial_python3.7_bin.tgz /home/ubuntu
        cd /usr/local/lib
        tar -czvf xenial_python3.7_lib.tgz python3.7 pkgconfig libpython3.so libpython3.7m.so.1.0 libpython3.7m.so
        mv xenial_python3.7_lib.tgz /home/ubuntu

    .. note::

        These files may differ depending on your installed version or system configuration.

.. seealso::

    For other guides on installing Python see:

        * The Python documentation: https://devguide.python.org/setup/
        * Real Python's Python 3 Installation & Setup Guide: https://realpython.com/installing-python/#how-to-build-python-from-source-code

*****************
Available Objects
*****************

.. automodule:: utilities.python
    :members:
    :undoc-members:
    :special-members:
    :private-members:
    :show-inheritance:
    :exclude-members: __dict__,__weakref__,__module__

