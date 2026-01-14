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
    if cgroup_name == "test_cgroup_a":
        return ["/tmp/test.pid"]
    # ...


def get_zk_host():
    return "127.0.0.1:2181,1.2.3.4:2181"


argkv = {
    "cgroup_dir": "/sys/fs/cgroup",
    "get_cgroup_pid_file": get_cgroup_pid_file,
    "get_zk_host": get_zk_host,
    "zk_prefix": "/cluser_a/service_rank",
    "zk_auth_data": [("digest", "super:123456")],
    "communicate_ip": "127.0.0.1",
    "communicate_port": "3344",
}

manager.run(**argkv)

argkv = {
    "cgroup_dir": "/sys/fs/cgroup",
    "get_zk_host": get_zk_host,
    "zk_prefix": "/cluser_a/service_rank",
    "zk_auth_data": [("digest", "super:123456")],
}
cgexec_arg = manager.get_cgexec_arg(["test_cgroup_a"], **argkv)

# return like:
# {
#     'test_cgroup_a': '-g cpu:test_cgroup_a',
# }
