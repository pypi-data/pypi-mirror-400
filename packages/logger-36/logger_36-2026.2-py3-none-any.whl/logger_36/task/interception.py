"""
Implement functions for warning and logging interceptions.

SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import logging as l
from pathlib import Path as path_t

from logger_36.constant.logger import WARNING_TYPE_COMPILED_PATTERN
from logger_36.hint.handle import logger_handle_h


def HandleForWarnings(interceptor: l.Logger, /) -> logger_handle_h:
    """
    Create a custom handle function for intercepting Python warnings.

    Generates a closure that parses warning messages, extracts relevant
    information, and routes them through the interceptor logger with
    enhanced formatting.

    Args:
        interceptor (l.Logger): The logger instance that should receive
            intercepted warning messages.

    Returns:
        logger_handle_h: A handle function suitable for assignment to a
            logger's handle attribute.

    Note:
        The generated function expects warning messages in Python's default
        warning format. If the format doesn't match, the warning is logged
        as-is without special parsing.

        Extracted information includes:
        - Source file path
        - Line number
        - Warning category/type
        - Warning message (cleaned of code snippets)

    Example:
        >>> import types
        >>> from logger_36 import L
        >>> L.MakeRich()
        >>> warning_logger = l.getLogger("py.warnings")
        >>> warning_logger.handle = types.MethodType(
        ...     HandleForWarnings(L), warning_logger
        ... )
    """

    def handle_p(_: l.Logger, record: l.LogRecord, /) -> None:
        """
        Handle a warning log record.

        Args:
            _ (l.Logger): The original warning logger (unused).
            record (l.LogRecord): The warning record to process.
        """
        pieces = WARNING_TYPE_COMPILED_PATTERN.match(record.msg)
        if pieces is None:
            # The warning message does not follow the default format.
            interceptor.handle(record)
            return

        GetPiece = pieces.group
        path = GetPiece(1)
        line = GetPiece(2)
        kind = GetPiece(3)
        message = GetPiece(4)

        path_as_t = path_t(path)
        line = int(line)
        line_content = path_as_t.read_text().splitlines()[line - 1]
        message = message.replace(line_content.strip(), "").strip()

        duplicate = l.makeLogRecord(record.__dict__)
        duplicate.msg = f"{kind}: {message}"
        duplicate.pathname = path
        duplicate.module = path_as_t.stem
        duplicate.funcName = "<function>"
        duplicate.lineno = line

        interceptor.handle(duplicate)

    return handle_p


def HandleForInterceptions(
    intercepted: l.Logger, interceptor: l.Logger, /
) -> logger_handle_h:
    """
    Create a custom handle function for intercepting logs from another logger.

    Generates a closure that duplicates log records and routes them through
    the interceptor logger with a suffix indicating the source logger.

    Args:
        intercepted (l.Logger): The logger whose messages are being intercepted.
        interceptor (l.Logger): The logger instance that should receive
            intercepted messages.

    Returns:
        logger_handle_h: A handle function suitable for assignment to a
            logger's handle attribute.

    Note:
        The intercepted logger's name is appended to messages as ":name:"
        to identify the source of the log.

    Example:
        >>> import types
        >>> from logger_36 import L
        >>> L.MakeRich()
        >>> other_logger = l.getLogger("mymodule")
        >>> other_logger.handle = types.MethodType(
        ...     HandleForInterceptions(other_logger, L), other_logger
        ... )
    """

    def handle_p(_: l.Logger, record: l.LogRecord, /) -> None:
        """
        Handle an intercepted log record.

        Args:
            _ (l.Logger): The intercepted logger (unused).
            record (l.LogRecord): The record to intercept and forward.
        """
        duplicate = l.makeLogRecord(record.__dict__)
        duplicate.msg = f"{record.msg} :{intercepted.name}:"
        interceptor.handle(duplicate)

    return handle_p
