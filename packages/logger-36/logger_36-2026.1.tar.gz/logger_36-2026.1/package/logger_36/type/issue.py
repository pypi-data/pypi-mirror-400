"""
Issue instantiation function NewIssue.

SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import logging as l
import typing as h

from logger_36.config.issue import ISSUE_BASE_CONTEXT
from logger_36.constant.issue import ISSUE_LEVEL_SEPARATOR
from logger_36.extension.sentinel import NOT_PASSED
from logger_36.hint.message import expected_op_h
from logger_36.task.format.message import MessageWithActualExpected

issue_t = str


def NewIssue(
    context: str,
    separator: str,
    message: str,
    /,
    *,
    level: int = l.ERROR,
    actual: h.Any = NOT_PASSED,
    expected: h.Any | None = None,
    expected_is_choices: bool = False,
    expected_op: expected_op_h = "=",
    with_final_dot: bool = True,
) -> tuple[issue_t, bool]:
    """Generate a new issue string based on the provided context, separator, message,
    and other optional parameters.

    This function constructs an issue string by combining the given context, separator,
    and formatted message. It also handles the inclusion of actual and expected values
    in the message if provided. The level parameter specifies the severity level of the
    issue, defaulting to logging.ERROR if not specified. The function returns a tuple
    containing the final issue string and a boolean indicating whether the message
    included actual and expected values.

    Args:
        context (str): The context or type of the issue. Must be a non-empty string; if
            empty, defaults to `ISSUE_BASE_CONTEXT`.
        separator (str): Separator used to join different parts of the issue message.
        message (str): Main text of the issue message.
        level (int, optional): Severity level of the issue (logging constants like
            `logging.ERROR`, `logging.WARNING`, etc.). Defaults to `logging.ERROR`.
        actual (h.Any, optional): Actual value to include in the message. If not
            provided or set to `NOT_PASSED`, it will be omitted. Default is
            `NOT_PASSED`.
        expected (h.Any | None, optional): Expected value to include in the message. Can
            be a single value or multiple choices. Defaults to `None`.
        expected_is_choices (bool, optional): Whether the expected value represents
            multiple choices (e.g., "in [1,2,3]"). Defaults to `False`.
        expected_op (expected_op_h, optional): Operation symbol for comparing actual and
            expected values (e.g., "=", "<>", ">", "<"). Default is `"="`.
        with_final_dot (bool, optional): Whether to append a final dot (`.`) at the end
            of the message. Defaults to `True`.

    Returns:
        tuple[issue_t, bool]: A tuple containing:
            - The formatted issue string.
            - A boolean indicating whether actual/expected values were included in the
            message.

    Raises:
        ValueError: If:
            - `context` is not a non-empty string or cannot be defaulted.
            - `separator` is not a valid string.
            - `level` is not a valid logging level constant.
            - Conflicting parameters (e.g., `expected_is_choices=True` but no choices
            are provided).
    """
    if context.__len__() == 0:
        context = ISSUE_BASE_CONTEXT
    message, has_actual_expected = MessageWithActualExpected(
        message,
        actual=actual,
        expected=expected,
        expected_is_choices=expected_is_choices,
        expected_op=expected_op,
        with_final_dot=with_final_dot,
    )

    return (
        f"{level}{ISSUE_LEVEL_SEPARATOR}{context}{separator}{message}",
        has_actual_expected,
    )
