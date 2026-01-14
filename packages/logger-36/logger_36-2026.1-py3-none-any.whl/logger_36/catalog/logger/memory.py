"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

from logger_36.config.memory import LENGTH_100, MAX_N_SAMPLES
from logger_36.constant.system import MAIN_PROCESS_NAME
from logger_36.hint.memory import storage_units_h
from logger_36.instance.logger import L
from logger_36.task.format.memory import FormattedUsage, UsageBar
from logger_36.task.format.message import MessageWithActualExpected
from logger_36.type.logger import logger_t


def LogMemoryUsages(
    *,
    unit: storage_units_h | None = "a",
    decimals: int | None = 1,
    max_n_samples: int | None = MAX_N_SAMPLES,
    length_100: int = LENGTH_100,
    logger: logger_t = L,
) -> None:
    """"""
    assert unit in h.get_args(storage_units_h)

    if (not hasattr(logger, "memory_usages")) or (logger.memory_usages.__len__() == 0):
        return

    title = LogMaximumMemoryUsage(
        unit=unit, decimals=decimals, only_return_message=True, logger=logger
    )

    several_processes_present = False
    per_where = {}
    for where, process, usage, total in logger.memory_usages:
        if process == MAIN_PROCESS_NAME:
            educated_where = where
        else:
            educated_where = f"{where}#{process}"
            several_processes_present = True
        current = per_where.get(educated_where, (0, 0))
        per_where[educated_where] = (max(current[0], usage), max(current[1], total))
    where_s, usages_and_totals = list(per_where.keys()), tuple(per_where.values())
    usages, totals = tuple(zip(*usages_and_totals))
    usages = list(usages)
    totals = list(totals)

    if isinstance(max_n_samples, int):
        if max_n_samples < 1:
            raise ValueError(
                MessageWithActualExpected(
                    "Invalid maximum number of samples",
                    actual=max_n_samples,
                    expected=1,
                    expected_op=">=",
                )[0]
            )

        while totals.__len__() > max_n_samples:
            minimum = min(totals)
            m_idx = totals.index(minimum)
            del where_s[m_idx]
            del usages[m_idx]
            del totals[m_idx]

    max_total_usage = max(totals)
    if max_total_usage <= 0:
        max_total_usage = max(usages)

    totals_as_str = tuple(f"{_:_}" for _ in totals)
    max_where_length = max(map(len, where_s))
    max_total_length = max(map(len, totals_as_str))
    if several_processes_present:
        usages_as_str = tuple(f" #{_:_}" for _ in usages)
        max_usage_length = max(map(len, usages_as_str))
    else:
        usages_as_str = usages.__len__() * ("",)
        max_usage_length = 0

    plot = []
    for where, usage, total, usage_as_str, total_as_str in zip(
        where_s, usages, totals, usages_as_str, totals_as_str
    ):
        bar = UsageBar(max(usage, total), max_total_usage, length_100=length_100)
        plot.append(
            f"{where:{max_where_length}} "
            f"{bar:{length_100}} "
            f"{total_as_str: >{max_total_length}}"
            f"{usage_as_str: >{max_usage_length}}"
        )
    plot = "\n".join(plot)

    logger.info(f"{title}\n{plot}")


def LogMaximumMemoryUsage(
    *,
    unit: storage_units_h | None = "a",
    decimals: int | None = 1,
    only_return_message: bool = False,
    logger: logger_t = L,
) -> str | None:
    """
    unit: b or None=bytes, k=kilo, m=mega, g=giga, a=auto
    """
    assert unit in h.get_args(storage_units_h)

    if (not hasattr(logger, "memory_usages")) or (logger.memory_usages.__len__() == 0):
        return None

    where, *_, max_usage = logger.max_memory_usage_full
    value, unit = FormattedUsage(max_usage, unit=unit, decimals=decimals)
    message = f"Max. Memory Usage: {value}{unit} near {where}"

    if only_return_message:
        return message

    logger.info(message)
    return None
