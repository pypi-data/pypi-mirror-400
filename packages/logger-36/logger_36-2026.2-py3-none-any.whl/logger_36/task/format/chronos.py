"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from datetime import datetime as date_time_t

from logger_36.config.message import ELAPSED_TIME_SEPARATOR
from logger_36.constant.chronos import START_DATE_TIME
from logger_36.constant.message import TIME_LENGTH


def FormattedElapsedTime(
    now: date_time_t,
    /,
    *,
    reference: date_time_t = START_DATE_TIME,
    with_separator: bool = True,
) -> str:
    """"""
    output = str(now - reference)

    if output.startswith("0:"):
        output = output[2:]
    while output.startswith("00:"):
        output = output[3:]
    if output[0] == "0":
        output = output[1:]

    if with_separator:
        output = ELAPSED_TIME_SEPARATOR + output

    if output.__len__() > TIME_LENGTH:
        return output[:TIME_LENGTH]
    return output
