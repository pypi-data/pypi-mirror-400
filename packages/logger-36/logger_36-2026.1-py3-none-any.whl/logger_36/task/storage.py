"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import logging as l
import typing as h
from io import IOBase as io_base_t
from pathlib import Path as path_t

from logger_36.config.rule import RULE_CHARACTER
from logger_36.constant.error import CANNOT_SAVE_RECORDS
from logger_36.constant.html import (
    BODY_PLACEHOLDER,
    HTML_SUFFIX,
    MINIMAL_HTML,
    TITLE_PLACEHOLDER,
)
from logger_36.constant.message import CONTEXT_LENGTH_p_1
from logger_36.extension.file import NewUniqueName
from logger_36.hint.record import IsRecordsAndLayout
from logger_36.hint.storage import layout_h
from logger_36.instance.logger import L
from logger_36.type.logger import logger_t
from logger_36.type.theme import theme_t


def SaveLOG(
    path: str | path_t | io_base_t | None = None,
    *,
    layout: layout_h = "raw",
    theme: str | theme_t | None = None,
    handler: l.Handler | None = None,
    logger: logger_t = L,
) -> None:
    """
    From first console handler found.
    """
    assert layout in h.get_args(layout_h)

    if handler is None:
        records, record_layout = logger_t.Records(logger)
    else:
        records_and_layout = getattr(handler, "records", None)
        if IsRecordsAndLayout(records_and_layout):
            records, record_layout = records_and_layout
        else:
            records = record_layout = None

    if records is None:
        logger.warning(
            f"{CANNOT_SAVE_RECORDS}: No handlers with recording capability found"
        )
        return
    if records.__len__() == 0:
        return

    if (record_layout == "message") and (layout == "html"):
        if theme is None:
            theme = theme_t.NewDefault("html", "light")
        elif isinstance(theme, str):
            theme = theme_t.NewDefaultFromStr(theme)
        messages = map(lambda _: _HTMLMessageFromRecord(_, theme), records)
    else:
        messages = map(lambda _: str(_[1]), records)
    content = "\n".join(messages)

    if layout == "html":
        content = MINIMAL_HTML.replace(TITLE_PLACEHOLDER, logger.name).replace(
            BODY_PLACEHOLDER, content
        )

    if path is None:
        path = logger_t.StoragePath(logger, "report", suffix=HTML_SUFFIX)
        logger.info(f'Saving LOG as HTML in "{path}"')
    elif isinstance(path, str | path_t):
        path = path_t(path)  # Possibly "redundant".
        if path.exists():
            existing = path
            path = NewUniqueName(existing)
            logger.warning(
                f'File "{existing}" already exists: '
                f'Saving LOG as HTML in "{path}" instead'
            )
    else:
        path.write(content)
        return

    with open(path, "w") as accessor:
        accessor.write(content)


def _HTMLMessageFromRecord(record: tuple[int, str], theme: theme_t, /) -> str:
    """"""
    level, message = record
    if message.startswith(RULE_CHARACTER):
        return f'<span style="color:{theme.rule};">{message}</span>'

    context = message[:CONTEXT_LENGTH_p_1]
    message = message[CONTEXT_LENGTH_p_1:]
    color = theme.text
    color_context = theme.level[level]

    return (
        f'<span style="color:{color};">'
        f'<span style="color:{color_context};">{context}</span>'
        f"{message}</span>"
    )
