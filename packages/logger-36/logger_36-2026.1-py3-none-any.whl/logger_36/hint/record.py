"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import logging as l
import typing as h

layout_h = h.Literal["dict", "json", "message", "raw"]

record_raw_h = dict | str | l.LogRecord
record_h = tuple[int, record_raw_h]  # First item=level.
records_h = list[record_h]


def IsARecord(checked: h.Any, /) -> bool:
    """"""
    return (
        isinstance(checked, tuple)
        and (checked.__len__() == 2)
        and isinstance(checked[0], int)
        and isinstance(checked[1], record_raw_h)
    )


def AreRecords(checked: h.Any, /) -> bool:
    """"""
    return isinstance(checked, list | tuple) and (
        (checked.__len__() == 0) or all(map(IsARecord, checked))
    )


def IsRecordsAndLayout(checked: h.Any, /) -> bool:
    """"""
    return (
        isinstance(checked, tuple)
        and (checked.__len__() == 2)
        and isinstance(checked[1], str)
        and (checked[1] in h.get_args(layout_h))
        and AreRecords(checked[0])
    )
