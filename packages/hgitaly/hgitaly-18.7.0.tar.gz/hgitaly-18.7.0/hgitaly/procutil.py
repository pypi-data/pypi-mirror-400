import os
import psutil


def is_current_service_process(pid):
    """Determine whether the given pid is part of the current HGitaly service.

    For now, the logic is that other processes from the same HGitaly service
    are expected to be siblings of the current process, unless in the special
    case where HGitaly is started direcly (not from RHGitaly's sidecar),
    hence for debugging purposes or from tests.
    """
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return False
    return proc.ppid() == os.getppid()
