"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

try:
    from psutil import Process as process_t  # noqa
    from psutil import NoSuchProcess  # noqa
except ModuleNotFoundError:
    process_t = None


def CanCheckUsage() -> bool:
    """"""
    return process_t is not None


def CurrentUsage(
    *, process: h.Any | None = None, root_pid: int | None = None
) -> tuple[int, int]:
    """
    process: Any object with a "pid" attribute (e.g., multiprocessing and psutil process
    classes).
    """
    if process_t is None:
        return -1, -1

    if process is None:
        process = process_t()
    else:
        try:
            process = process_t(process.pid)
        except NoSuchProcess:
            process = None

    if process is None:
        return -1, -1

    usage = process.memory_info().rss

    if root_pid is None:
        return usage, -1

    try:
        root_process = process_t(root_pid)
        subprocesses = root_process.children(recursive=True)
    except NoSuchProcess:
        total = -1
    else:
        total = usage
        for subprocess in subprocesses:
            try:
                sub_usage = subprocess.memory_info().rss
            except NoSuchProcess:  # Just in case.
                pass
            else:
                total += sub_usage

    return usage, total
