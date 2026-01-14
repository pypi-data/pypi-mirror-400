"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import difflib as diff
import typing as h

from logger_36.extension.sentinel import NOT_PASSED
from logger_36.hint.message import expected_op_h


def MessageWithActualExpected(
    message: str,
    /,
    *,
    actual: h.Any = NOT_PASSED,
    expected: h.Any | None = None,
    expected_is_choices: bool = False,
    expected_op: expected_op_h = "=",
    with_final_dot: bool = True,
) -> tuple[str, bool]:
    """
    Second return: has_actual_expected.
    """
    if actual is NOT_PASSED:
        if with_final_dot:
            if message[-1] != ".":
                message += "."
        elif message[-1] == ".":
            message = message[:-1]

        return message, False

    if message[-1] == ".":
        message = message[:-1]
    expected = _FormattedExpected(expected_op, expected, expected_is_choices, actual)
    if with_final_dot:
        dot = "."
    else:
        dot = ""

    if isinstance(actual, type):
        actual = actual.__name__
    else:
        actual = f"{actual}:{type(actual).__name__}"

    return f"{message}: Actual={actual}; {expected}{dot}", True


def _FormattedExpected(
    operator: str, expected: h.Any, expected_is_choices: bool, actual: h.Any, /
) -> str:
    """"""
    if isinstance(expected, h.Sequence) and expected_is_choices:
        close_matches = diff.get_close_matches(actual, expected)
        if close_matches.__len__() > 0:
            close_matches = ", ".join(close_matches)
            return f"Close matche(s): {close_matches}"
        else:
            expected = ", ".join(map(str, expected))
            return f"Valid values: {expected}"

    if isinstance(expected, type):
        return f"Expected{operator}{expected.__name__}"

    if operator == "=":
        stripe = f":{type(expected).__name__}"
    else:
        stripe = ""
        if operator == ":":
            operator = ": "
    return f"Expected{operator}{expected}{stripe}"
