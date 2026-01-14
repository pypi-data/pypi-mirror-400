import logging
import os
import time

import redis
from kazoo.client import KazooClient

import k3thread
import k3utfjson
import k3zkutil
from k3cgrouparch import account
from k3cgrouparch import cgroup_manager
from k3cgrouparch import communicate

logger = logging.getLogger(__name__)


global_value = {}


def init_redis_client(context):
    client = redis.StrictRedis(context["redis_ip"], context["redis_port"])
    context["redis_client"] = client


def get_zk_client(context):
    host = context["get_zk_host"]()
    zk_client = KazooClient(
        hosts=host, timeout=3.0, randomize_hosts=True, auth_data=context["zk_auth_data"], logger=logger
    )

    zk_client.start()

    return zk_client


def update_conf(event):
    logger.info("update conf triggered at: %f" % time.time())

    context = global_value["context"]

    zk_path = "%s/arch_conf" % context["zk_prefix"]

    while True:
        try:
            zk_client = context["zk_client"]
            resp = zk_client.get(zk_path, watch=update_conf)
            break

        except Exception as e:
            logger.exception("failed to get from zk: " + repr(e))
            time.sleep(5)

    context["arch_conf"] = {
        "version": resp[1].version,
        "value": k3utfjson.load(resp[0]),
    }

    logger.info("arch conf in zk changed at: %f, current verrsion: %d" % (time.time(), resp[1].version))

    cgroup_manager.build_all_subsystem_cgroup_arch(context)


def on_lost(stat):
    logger.warn("zk client on lost, stat is: %s, about to exit" % str(stat))
    os._exit(2)


def init_arch_conf(context):
    while True:
        try:
            if context["zk_client"] is None:
                context["zk_client"] = get_zk_client(context)
                context["zk_client"].add_listener(on_lost)

            zk_path = "%s/arch_conf" % context["zk_prefix"]
            resp = context["zk_client"].get(zk_path, watch=update_conf)

            context["arch_conf"] = {
                "version": resp[1].version,
                "value": k3utfjson.load(resp[0]),
            }

            return

        except Exception as e:
            logger.warn("failed to get arch conf from zk: %s" % repr(e))

            k3zkutil.close_zk(context["zk_client"])
            context["zk_client"] = None
            time.sleep(10)


def update_cgexec_arg(cgexec_arg, subsystem_name, cgroup_relative_path, cgroup_conf):
    sub_cgroup = cgroup_conf.get("sub_cgroup")
    if sub_cgroup is None:
        return

    for sub_cgroup_name, sub_cgroup_conf in sub_cgroup.items():
        sub_relative_path = cgroup_relative_path + "/" + sub_cgroup_name

        if sub_cgroup_name in cgexec_arg:
            cgexec_arg[sub_cgroup_name] += " -g %s:%s" % (subsystem_name, sub_relative_path)

        update_cgexec_arg(cgexec_arg, subsystem_name, sub_relative_path, sub_cgroup_conf)


def get_cgexec_arg(cgroup_names, **argkv):
    """
    This method used to get the argument used in `cgexec` command.
    :param cgroup_names: a list of cgroup names.
    :param argkv:the same as that in `manager.run`, but only `cgroup_dir`,
    `get_zk_host`, `zk_prefix`, `zk_auth_data` are needed.
    :return: A dict contains argument for `cgexec` of each input cgroup.
    """
    context = {
        "cgroup_dir": argkv.get("cgroup_dir", "/sys/fs/cgroup"),
        "get_zk_host": argkv["get_zk_host"],
        "zk_prefix": argkv["zk_prefix"],
        "zk_auth_data": argkv["zk_auth_data"],
    }

    cgexec_arg = {}
    for cgroup_name in cgroup_names:
        cgexec_arg[cgroup_name] = ""

    try:
        zk_client = get_zk_client(context)

        zk_path = "%s/arch_conf" % context["zk_prefix"]
        resp = zk_client.get(zk_path)

        k3zkutil.close_zk(zk_client)

        context["arch_conf"] = {
            "version": resp[1].version,
            "value": k3utfjson.load(resp[0]),
        }
        cgroup_manager.build_all_subsystem_cgroup_arch(context)

        arch_conf_value = context["arch_conf"]["value"]
        for subsystem_name, subsystem_conf in arch_conf_value.items():
            cgroup_relative_path = ""
            cgroup_conf = subsystem_conf
            update_cgexec_arg(cgexec_arg, subsystem_name, cgroup_relative_path, cgroup_conf)

        return cgexec_arg

    except Exception as e:
        logger.exception("failed to get cgexec arg: " + repr(e))
        return cgexec_arg


def run(**argkv):
    """
    This function read configuration from zookeeper and build the cgroup
    directory tree accordingly, it also  update cgroup pid periodically.
    Every second it save usage info of each cgroup in redis, you can read
    usage info through websocket protocol.

    :param argkv:
    `get_cgroup_pid_file`:
    a callback function, the argument is the cgroup name, and it
    should return a list of pid files. Required.

    `get_zk_host`:
    a callback function, should return zookeeper hosts, for example:
    '127.0.0.1:2181,1.2.3.4:2181'. Required.

    `zk_prefix`:
    specify the zookeeper key prefix'. Required.

    `zk_auth_data`:
    specify zookeeper auth data, for example: `[('digest', 'super:123456')]`.
    Required.

    `communicate_ip`:
    specify ip address the websocket server will bind. Default to '0.0.0.0'.

    `communicate_port`:
    specify port the websocket server will bind. Default to 43409.

    `tasks_update_interval`:
    set cgroup tasks file update interval in seconds. Default to 30.

    `cgroup_dir`:
    the mount point of the cgroup filesystem, default to '/sys/fs/cgroup'.

    `redis_ip`:
    ip of the redis server. Required.

    `redis_port`:
    port of the redis server. Required.

    `redis_prefix`:
    the key prefix to use when saving usage info into redis.

    `redis_expire_time`:
    we only keep recent usage info in redis, this specify the
    expire time in seconds of usage info data in redis.  Default to 300.

    `protected_cgroup`:
    specify a list of cgroup names that you do not allow the manager
    to touch, or the manager will remove all cgroups that are not
    in the conf. Optional.
    :return: Not return
    """
    context = {
        "get_cgroup_pid_file": argkv["get_cgroup_pid_file"],
        "cgroup_dir": argkv.get("cgroup_dir", "/sys/fs/cgroup"),
        "communicate_ip": argkv.get("communicate_ip", "0.0.0.0"),
        "communicate_port": argkv.get("communicate_port", 43409),
        "tasks_update_interval": argkv.get("tasks_update_interval", 30),
        "redis_ip": argkv["redis_ip"],
        "redis_port": argkv["redis_port"],
        "redis_prefix": argkv.get("redis_prefix", "cgroup_arch"),
        "redis_client": None,
        "redis_expire_time": argkv.get("redis_expire_time", 60 * 5),
        "get_zk_host": argkv["get_zk_host"],
        "zk_prefix": argkv["zk_prefix"],
        "zk_auth_data": argkv["zk_auth_data"],
        "zk_client": None,
        "protected_cgroup": argkv.get("protected_cgroup"),
        "arch_conf": None,
    }

    init_redis_client(context)
    init_arch_conf(context)

    global_value["context"] = context

    cgroup_manager.build_all_subsystem_cgroup_arch(context)

    cgroup_manager.set_cgroup(context)

    cgroup_manager.reset_statistics(context)

    k3thread.start(account.run, args=(context,))

    k3thread.start(cgroup_manager.loop_set_cgroup, args=(context,))

    communicate.run(context, ip=context["communicate_ip"], port=context["communicate_port"])
