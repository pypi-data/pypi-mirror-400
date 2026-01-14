# k3cgrouparch

[![Action-CI](https://github.com/pykit3/k3cgrouparch/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3cgrouparch/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3cgrouparch/badge/?version=stable)](https://k3cgrouparch.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3cgrouparch)](https://pypi.org/project/k3cgrouparch)

This lib is used to set up cgroup directory tree according to configuration saved in zookeeper, and add pid to cgroup accordingly.

k3cgrouparch is a component of [pykit3] project: a python3 toolkit set.


#   Name

cgrouparch

A python lib used to build cgroup directory tree, add set cgroup pid.

#   Status

This library is considered production ready.

#   Description

This lib is used to set up cgroup directory tree according to
configuration saved in zookeeper, and add pid to cgroup accordingly.




# Install

```
pip install k3cgrouparch
```

# Synopsis

```python

# {
#     'cpu': {
#         'sub_cgroup': {
#             'test_cgroup_a': {
#                 'conf': {
#                     'share': 1024,
#                 },
#             },
#             'test_cgroup_b': {
#                 'conf': {
#                     'share': 100,
#                 },
#                 'sub_cgroup': {
#                     'test_cgroup_b_sub1': {
#                         'conf': {
#                             'share': 200,
#                         },
#                     },
#                 },
#             },
#         },
#     },
# }

from k3cgrouparch import manager


def get_cgroup_pid_file(cgroup_name):
    if cgroup_name == 'test_cgroup_a':
        return ['/tmp/test.pid']
    # ...


def get_zk_host():
    return '127.0.0.1:2181,1.2.3.4:2181'


argkv = {
    'cgroup_dir': '/sys/fs/cgroup',
    'get_cgroup_pid_file': get_cgroup_pid_file,
    'get_zk_host': get_zk_host,
    'zk_prefix': '/cluser_a/service_rank',
    'zk_auth_data': [('digest', 'super:123456')],
    'communicate_ip': '127.0.0.1',
    'communicate_port': '3344',
}

manager.run(**argkv)

argkv = {
    'cgroup_dir': '/sys/fs/cgroup',
    'get_zk_host': get_zk_host,
    'zk_prefix': '/cluser_a/service_rank',
    'zk_auth_data': [('digest', 'super:123456')],
}
cgexec_arg = manager.get_cgexec_arg(['test_cgroup_a'], **argkv)

# return like:
# {
#     'test_cgroup_a': '-g cpu:test_cgroup_a',
# }

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3