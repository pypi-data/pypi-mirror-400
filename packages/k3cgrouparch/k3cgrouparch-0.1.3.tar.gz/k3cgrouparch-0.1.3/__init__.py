"""
#   Name

cgrouparch

A python lib used to build cgroup directory tree, add set cgroup pid.

#   Status

This library is considered production ready.

#   Description

This lib is used to set up cgroup directory tree according to
configuration saved in zookeeper, and add pid to cgroup accordingly.

"""

# from .proc import CalledProcessError
# from .proc import ProcError

from importlib.metadata import version

__version__ = version("k3cgrouparch")
