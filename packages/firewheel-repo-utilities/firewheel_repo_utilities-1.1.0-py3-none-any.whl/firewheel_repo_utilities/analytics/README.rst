.. _analytics_mc:

#########
analytics
#########

The Analytics MC provides FIREWHEEL experiments with tools for monitoring and collecting data on each VM during an experiment.
By decorating a :py:class:`Vertex <firewheel.control.experiment_graph.Vertex>` with the Analytics MC, that :py:class:`Vertex <firewheel.control.experiment_graph.Vertex>` gains access to methods that will schedule different analytic capabilities to be executed at the start of an experiment (time == 1).
After decorating your :py:class:`Vertex <firewheel.control.experiment_graph.Vertex>`, you will need to call the newly available methods depending on the kind of data which should be collected.

********************
Current capabilities
********************

All the methods are documented in :py:class:`analytics.Analytics`, but for ease of use we list a few of the more useful methods here.
Some methods are Linux dependent (e.g. `strace <https://strace.io/>`__) while others depend on `psutil <https://pypi.org/project/psutil/>`__.

Linux dependent
===============

* :py:meth:`analytics.Analytics.run_tcpdump`
    Runs `tcpdump <https://www.tcpdump.org/>`_ on the VM to capture any network traffic during the positive time of the experiment.

    **Default command:** ``tcpdump -U -w /opt/analytics/pcaps/tmp.pcap -Z root``

* :py:meth:`analytics.Analytics.add_port_tracking`
    Runs ``netstat -tulpn`` every ``<refresh_interval_sec>`` seconds and tracks the changes between each call.
    One of three possible headers will be outputted with each log: ``INITIAL``, ``ADDED``, or ``DELETED``.
    These headers are used to track the state of each line outputted by each `netstat <https://linux.die.net/man/8/netstat>`__ execution.

* :py:meth:`analytics.Analytics.tailf_dir`
    Given a positive ( >= 1 ) time, a target directory, and a regex to match against, this method schedules a script that will execute a ``tail -f`` on any file created in the target directory that matches on the regex.
    This script was designed for use by the :py:meth:`strace <analytics.Analytics.strace>` method so that each new ``.strace`` file will be reported back to the VM Resource Management logs on the :ref:`cluster-compute-nodes` (see :ref:`vmr-output` more details).
    Each outputted line from the ``tail -f`` is wrapped in the format used by the :ref:`JSONLogger` (see the :ref:`utilities.python_mc`), so that it is also placed into the VM Resource ``.json`` logs.

* :py:meth:`analytics.Analytics.strace`
    This script utilizes `pgrep <https://linux.die.net/man/1/pgrep>`_ and a provided regular expression to determine the processes to attach `strace <https://strace.io/>`__.
    The programmer could, instead of using this tool, schedule the `strace <https://strace.io/>`__ with the original execution of the process they want to track, which would avoid the need to find and attach to the process after the fact.
    However, this tool was designed in order to avoid that exact scenario.

    **Default command:** ``strace -ff -tt -s 1024 -o /opt/analytics/traces/(no_tailf_dirs|tailf_dirs)/<time>/`` i.e. ``strace -ff -tt -s 1024 -o /opt/analytics/traces/tailf_dirs/10/``


`psutil <https://pypi.org/project/psutil/>`__ dependent
=======================================================

* :py:meth:`analytics.Analytics.add_network_io_tracking`
    Uses `psutil <https://pypi.org/project/psutil/>`__ to obtain network IO counters for each NIC on the VM every ``<refresh_interval_sec>`` seconds.
    Outputs these data to a file on the VM.
    Collects the following data for **each network interface** on each VM:

    * bytes received
    * bytes sent
    * drop in
    * drop out
    * err in
    * err out
    * packets received
    * packets sent

  See https://psutil.readthedocs.io/en/latest/#psutil.net_io_counters for more details.

* :py:meth:`analytics.Analytics.add_system_memory_tracking`
    Uses `psutil <https://pypi.org/project/psutil/>`__ to obtain the current virtual memory state on the VM every ``<refresh_interval_sec>`` seconds.
    Outputs these data to a file on the VM.
    Collects the following data for each VM:

    * active
    * available
    * buffers
    * cached
    * free
    * inactive
    * percent
    * shared
    * slab
    * total
    * used

  See https://psutil.readthedocs.io/en/latest/#psutil.virtual_memory for more details.

* :py:meth:`analytics.Analytics.add_cpu_tracking`
    Uses `psutil <https://pypi.org/project/psutil/>`__ to obtain the current system-wide CPU utilization as a percent for each CPU on the VM every ``<refresh_interval_sec>`` seconds.
    Outputs these data to a file on the VM.
    Collects the following data for **each CPU** on the VM, if available:

    * percent

  See https://psutil.readthedocs.io/en/latest/#psutil.cpu_percent for more details.

* :py:meth:`analytics.Analytics.add_disk_usage_tracking`
    Uses `psutil <https://pypi.org/project/psutil/>`__ to obtain the disk usage per partition mount point on the VM every ``<refresh_interval_sec>`` seconds.
    Outputs these data to a file on the VM.
    Collects the following data for **each disk mount point** on the VM:

    * free
    * percent
    * total
    * used

  See https://psutil.readthedocs.io/en/latest/#psutil.disk_usage for more details.

* :py:meth:`analytics.Analytics.add_disk_io_tracking`
    Uses `psutil <https://pypi.org/project/psutil/>`__ to obtain disk IO counters for each partition on the VM every ``<refresh_interval_sec>`` seconds.
    Outputs these data to a file on the VM.
    Collects the following data for **each disk partition** on the VM over time:

    * busy time
    * read bytes
    * read count
    * read merged count
    * write bytes
    * write count
    * write merged count
    * write time

  See https://psutil.readthedocs.io/en/latest/#psutil.disk_io_counters for more details.

Future Capabilities
===================

We would like to be able to track the files that are dropped during the execution of an experiment.
This would be great as we could see if any artifacts are stored or left behind after execution.
A difficulty with this is knowing where to track for new file creation, as tracking the entire drive doesn't seem like the smartest idea.

FIREWHEEL currently uses minimega for launching VMs.
minimega has a suite of tools used to collect data similar to what this model component provides, but has additional features including VNC capture/replay.
Users should visit https://minimega.org/articles/api.article to learn more about the possible ways to collect experiment data.


As an example for how to use these tools in your experiment, the below snippets are provided.

*******
Example
*******

``model_component_objects.py``
==============================

.. code-block:: python

    from analytics import Analytics

    @require_class(Analytics)
    class MyClass:

        def __init__(self):
            print("This is my test class!")

        def add_analytics(self):
            self.run_tcpdump()
            self.add_system_memory_tracking(refresh_interval_sec=10)


``plugin.py``
=============

.. code-block:: python

    from firewheel.control.experiment_graph import AbstractPlugin, Vertex
    from my_model_component import MyClass

    class MyModelComponent(AbstractPlugin):

        def run(self):
            my_vm = Vertex(self.g, "myclass_vm")
            my_vm.decorate(MyClass)
            my_vm.add_analytics()


You will also have to include "analytics" in your ``MANIFEST`` file's list of model_component dependencies.
Below is not a complete ``MANIFEST`` file, but just a snippet of one to demonstrate the necessary inclusion.

``MANIFEST``
============

.. code-block:: yaml

    name: my_model_component
    attributes:
        depends: []
        precedes: []
        provides: []
    model_components:
        depends:
        - analytics
        precedes: []
    model_component_objects: model_component_objects.py
    plugin: plugin.py


**Model Component Dependencies:**
    * :ref:`base_objects_mc`
    * :ref:`utilities.python_mc`


*****************
Available Objects
*****************

.. automodule:: analytics
    :members:
    :undoc-members:
    :special-members:
    :private-members:
    :show-inheritance:
    :exclude-members: __dict__,__weakref__,__module__

