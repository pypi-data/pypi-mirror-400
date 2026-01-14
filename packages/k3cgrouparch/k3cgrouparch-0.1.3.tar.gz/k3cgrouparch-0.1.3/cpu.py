import logging
import os

import k3fs
from k3cgrouparch import cgroup_util

logger = logging.getLogger(__name__)


def set_cgroup(cgroup_path, conf):
    if "share" not in conf:
        share = "1024"
    else:
        share = str(conf["share"])

    share_file = os.path.join(cgroup_path, "cpu.shares")

    k3fs.fwrite(share_file, share, fsync=False)
    logger.info("write: %s to file: %s" % (share, share_file))

    pids = conf.get("pids")

    if pids is None:
        return

    cgroup_util.add_pids(cgroup_path, pids)
    logger.info("add pids: %s to cgroup: %s" % (repr(pids), cgroup_path))


def reset_statistics(cgroup_path):
    usage_file = os.path.join(cgroup_path, "cpuacct.usage")
    k3fs.fwrite(usage_file, "0", fsync=False)


def account(cgroup_path):
    usage_file = os.path.join(cgroup_path, "cpuacct.usage")

    usage = int(k3fs.fread(usage_file).strip())

    return {
        "usage": usage,
    }
