from k3cgrouparch import blkio
from k3cgrouparch import cpu

subsystem = {
    "cpu": {
        "set_cgroup": cpu.set_cgroup,
        "reset_statistics": cpu.reset_statistics,
        "account": cpu.account,
    },
    "blkio": {
        "set_cgroup": blkio.set_cgroup,
        "reset_statistics": blkio.reset_statistics,
        "account": blkio.account,
    },
}
