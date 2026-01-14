"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import logging as l
import sys as s
import typing as h

from logger_36.type.handler import non_file_handler_t as base_t


class console_handler_t(base_t):
    @classmethod
    def New(
        cls,
        /,
        *,
        name: str | None = None,
        message_width: int = -1,
        level: int = l.NOTSET,
        **_,
    ) -> h.Self:
        """"""
        return cls(name, message_width, level, None)

    def emit(self, record: l.LogRecord, /) -> None:
        """"""
        s.__stdout__.write(self.MessageFromRecord(record) + "\n")
