"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import logging as l
import typing as h
from pathlib import Path as path_t

from logger_36.type.handler import file_handler_t as base_t


class file_handler_t(base_t):
    @classmethod
    def New(
        cls,
        /,
        *,
        name: str | None = None,
        message_width: int = -1,
        level: int = l.NOTSET,
        path: str | path_t | None = None,
        **_,
    ) -> h.Self:
        """"""
        return cls(name, message_width, level, path)

    def emit(self, record: l.LogRecord, /) -> None:
        """"""
        self.stream.write(self.MessageFromRecord(record) + "\n")
        self.stream.flush()
