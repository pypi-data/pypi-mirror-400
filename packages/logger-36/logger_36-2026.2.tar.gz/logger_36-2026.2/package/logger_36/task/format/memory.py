"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

from logger_36.hint.memory import storage_units_h
from logger_36.task.format.message import MessageWithActualExpected

_KILO_UNIT = 1000.0
_MEGA_UNIT = _KILO_UNIT * 1000.0
_GIGA_UNIT = _MEGA_UNIT * 1000.0

_BLOCKS_PARTIAL = ("", "▏", "▎", "▍", "▌", "▋", "▊")
_BLOCK_FULL = "▉"


def FormattedUsage(
    usage: int, /, *, unit: storage_units_h | None = "a", decimals: int | None = None
) -> tuple[int | float, str]:
    """
    unit: b or None=bytes, k=kilo, m=mega, g=giga, a=auto
    """
    assert unit in h.get_args(storage_units_h)

    if (unit is None) or (unit == "b"):
        value = usage
        unit = "B"
    elif unit == "k":
        value = _Rounded(usage / _KILO_UNIT, decimals)
        unit = "KB"
    elif unit == "m":
        value = _Rounded(usage / _MEGA_UNIT, decimals)
        unit = "MB"
    elif unit == "g":
        value = _Rounded(usage / _GIGA_UNIT, decimals)
        unit = "GB"
    else:  # unit == "a"
        value, unit = FormattedUsageWithAutoUnit(usage, decimals)

    return value, unit


def FormattedUsageWithAutoUnit(
    usage: int, decimals: int | None, /
) -> tuple[int | float, str]:
    """"""
    if usage > _GIGA_UNIT:
        return _Rounded(usage / _GIGA_UNIT, decimals), "GB"

    if usage > _MEGA_UNIT:
        return _Rounded(usage / _MEGA_UNIT, decimals), "MB"

    if usage > _KILO_UNIT:
        return _Rounded(usage / _KILO_UNIT, decimals), "KB"

    return usage, "B"


def UsageBar(
    usage: int | float, max_usage: int | float, /, *, length_100: int = 10
) -> str:
    """"""
    length = (usage / max_usage) * length_100
    n_full_s = int(length)
    return (
        n_full_s * _BLOCK_FULL
        + _BLOCKS_PARTIAL[int((2.0 / 3.0) * int(10 * (length - n_full_s)))]
    )


def _Rounded(value: float, decimals: int | None, /) -> int | float:
    """"""
    if decimals == 0:
        decimals = None

    return round(value, ndigits=decimals)
