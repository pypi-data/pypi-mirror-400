.. _utilities.nodejs_mc:

#################
utilities.nodejs
#################


*Provides an implementation of Node.js on a virtual machine.*

*****
Usage
*****

This model component provides a decorator for adding Node.js to a virtual machine.
Multiple versions of Node are provided as VM resources, each with a version specifier (e.g., ``node-v20.12.2-linux-x64``), and the Node version to use in an experiment can be provided by passing the version number as an argument to the decorator upon instantiation:

.. code-block:: python

            # ... plugin setup ...

            vertex.decorate(NodeJSVM, init_kwargs={"node_version": "20.12.2"})

Other less commonly used parameters may also be configured via the decorator, including the method of installation for the Node binaries (directly into ``/usr/local/bin`` or symlinked there) and whether or not ``npm`` should operate in offline mode (set to work offline by default).
See the :py:meth:`decorator constructor documentation <utilties.nodejs.NodeJSVM.__init__>` for more details.


**********************************************************
Extending the Model Component with New Versions of Node.js
**********************************************************

The supported versions of Node are listed below in the `VM Resources`_ section.
To use a different version of Node in the model component, download the binary from a source repository (e.g., `nodejs.org <https://nodejs.org/en/download/prebuilt-binaries>`_) and add it to the ``vm_resources`` directory.
Ensure that the binary is a ``*.tar.xz`` archive with a filename following the format ``node-v<Major>.<minor>.<patch>-linux-x64.tar.xz``.
This filename structure is the default for all binaries downloaded from the official Node.js repository and is required by the installer.
Note that only Linux binaries can be used, since the ``NodeJSVM`` decorator requires that the VM be an instance of ``UbuntuHost`` provided by the ``linux.ubuntu`` model component.
Once downloaded to the ``vm_resources`` directory, this new version of Node should be available as an argument to the decorator as described above (the ``MANIFEST`` already supports arbitrary ``.tar.xz`` VM resources and so should not need modification).

Since Node.js binaries should not be distributed with the repository, binaries that are to be permanently included with the MC should not be committed directly to the ``vm_resources`` directory.
Instead, update the ``INSTALL`` script to download the new binary from its source.
For binaries made available through the official Node.js website, simply add the new version of node along with its corresponding checksum in the ``DOWNLOAD SPECIFICATION`` section of the script:

.. code-block:: bash

        node_18_13_0=("18.13.0" "7f5d6922a91986ef059ba8a4396aa435440adacfe6fc6fab60a857c8f2cf5e7a")
        node_20_12_2=("20.12.2" "595272130310cbe12301430756f23d153f7ab95d00174c02adc11a2e3703d183")

        # Add new Node.js versions here, replacing terms in angle brackets
        node_<M>_<m>_<p>=("<Major>.<minor>.<patch>" "<sha256 checksum>");

        # Update the `node_versions` array to include the new version
        node_versions=(node_18_13_0 node_20_12_2 node_<M>_<m>_<p>)

To determine the checksum of a Node binary that can be verified by the ``INSTALL`` script, run the following:

.. code-block:: bash

        shasum -a 256 <node-binary>

Finally, update the list of VM resources here in the README.


******************************************************
Downloading Packages for Use in VMs Supoorting Node.js
******************************************************

This model component facilitates preparation of a VM to offer a supported version of Node.js.
However, when subsequent downstream model components rely on this MC so that they can use a Node package in a FIREWHEEL experiment, those downstream MCs will need to provide any additional package dependencies.
Since FIREWHEEL experiments typically operate offline, those package dependencies will likely be required to have been downloaded in advance.
The recommended approach for generating these dependencies is to acquire all necessary dependency content using the :ref:`VM Builder <helper_vm_builder>` utility in ``launch`` mode.
Then, using an Internet connection in the VM builder:

#. Install the appropriate version of Node.js. Ideally, this is the exact same version as the experiment.
#. Install the package dependencies using ``npm`` (installed with Node.js).
#. [Optional] Zip dependency files (e.g., ``package.json``, ``package-lock.json`` and ``node_modules`` files and directories) into a tar archive.
#. Use SCP to copy the files from the VM builder machine to the ``vm_resources`` directory in the model component repository on the machine being used for MC development. (Hint: Use the ``ip addr`` command on the builder VM to get the IP address of that machine.)
#. Indicate how the model component should handle the files. This may include updating the ``MANIFEST``, using the :py:meth:`linux.base_objects.LinuxHost.unpack_tar` or :py:meth:`base_objects.VMEndpoint.drop_file` methods. Packages may be dropped anywhere on the file system, with global packages typically stored in ``/usr/local/lib/node`` or ``/usr/local/lib/node_modules`` and local packages stored in any other directory of choice.


**Attribute Provides:**
    * ``nodejs``


**Model Component Dependencies:**
    * :ref:`linux.ubuntu`


************
VM Resources
************

* ``node-v18.13.0-linux-x64.tar.xz``
* ``node-v20.12.2-linux-x64.tar.xz``


*****************
Available Objects
*****************

.. automodule:: utilities.nodejs
    :members:
    :undoc-members:
    :special-members:
    :private-members:
    :show-inheritance:
    :exclude-members: __dict__,__weakref__,__module__

