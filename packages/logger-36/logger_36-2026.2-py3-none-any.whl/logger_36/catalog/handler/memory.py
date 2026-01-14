"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import json
import logging as l
import typing as h

from logger_36.hint.record import layout_h, records_h
from logger_36.type.handler import non_file_handler_t as base_t


class memory_handler_t(base_t):
    def __init__(
        self, name: str | None, message_width: int, level: int, layout: layout_h
    ) -> None:
        """"""
        assert layout in h.get_args(layout_h)

        base_t.__init__(self, name, message_width, level, None)

        self.layout = layout
        self._records: records_h = []

    @property
    def records(self) -> tuple[records_h | None, layout_h | None]:
        """"""
        return self._records, self.layout

    @classmethod
    def New(
        cls,
        /,
        *,
        name: str | None = None,
        message_width: int = -1,
        level: int = l.NOTSET,
        layout: layout_h = "message",
        **_,
    ) -> h.Self:
        """"""
        assert layout in h.get_args(layout_h)
        return cls(name, message_width, level, layout)

    def emit(self, record: l.LogRecord, /) -> None:
        """"""
        level = record.levelno

        if self.layout == "raw":
            pass
        elif self.layout == "dict":
            record = dict(record.__dict__)
        elif self.layout == "json":
            record = json.dumps(record.__dict__)
        else:
            record = self.MessageFromRecord(record)

        self._records.append((level, record))
