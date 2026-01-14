"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from datetime import datetime as date_time_t


def TimeStamp(*, precision: str = "microseconds") -> str:
    """
    precision: See documentation of date_time_t.isoformat.
    """
    return (
        date_time_t.now()
        .isoformat(timespec=precision)
        .replace(".", "_")
        .replace(":", "-")
        .replace("T", "_")
    )
