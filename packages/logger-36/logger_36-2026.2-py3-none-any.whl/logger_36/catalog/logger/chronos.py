"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from datetime import datetime as date_time_t

from logger_36.constant.chronos import FORMATTED_START_DATE_TIME, START_DATE_TIME
from logger_36.constant.record import SHOW_WHEN_ATTR, SHOW_WHERE_ATTR
from logger_36.constant.system import MAIN_PROCESS_NAME
from logger_36.instance.logger import L
from logger_36.task.format.chronos import FormattedElapsedTime
from logger_36.type.logger import logger_t

_START_NAME = "START"
_START_PLACEHOLDER = "..."  # Must not be longer than _START_NAME.
_END_NAME = "END"


def LogElapsedTime(*, logger: logger_t = L) -> None:
    """"""
    now = date_time_t.now()

    message = (
        f"Elapsed Time: {FormattedElapsedTime(now, with_separator=False)} "
        f"(since {FORMATTED_START_DATE_TIME})"
    )
    if logger.intermediate_times.__len__() > 0:
        intermediate_times_s = {}
        for name, process, date_time in logger.intermediate_times:
            value = (name, date_time)
            current = intermediate_times_s.get(process, None)
            if current is None:
                intermediate_times_s[process] = [value]
            else:
                current.append(value)

        process_names = sorted(intermediate_times_s.keys())
        del process_names[process_names.index(MAIN_PROCESS_NAME)]
        process_names = [MAIN_PROCESS_NAME] + process_names

        n_processes = intermediate_times_s.__len__()
        title = ""
        for process_name in process_names:
            intermediate_times = intermediate_times_s[process_name]
            intermediate_e_times = []
            for (start_name, start_time), (end_name, end_time) in zip(
                [(_START_NAME, START_DATE_TIME)] + intermediate_times,
                intermediate_times + [(_END_NAME, now)],
                strict=True,
            ):
                if start_name != _START_NAME:
                    start_name = _START_PLACEHOLDER
                e_time = FormattedElapsedTime(
                    end_time, reference=start_time, with_separator=False
                )
                intermediate_e_times.append((start_name, end_name, e_time))
            max_length_end = max(map(len, (_[1] for _ in intermediate_e_times)))
            intermediate_e_times = "\n    ".join(
                f"{_: <{_START_NAME.__len__()}} → {__: <{max_length_end}}   +{___}"
                for _, __, ___ in intermediate_e_times
            )
            if (n_processes > 1) or (process_name != MAIN_PROCESS_NAME):
                title = f"\n--- {process_name} ---"
            message += f"{title}\n    " + intermediate_e_times
        logger.intermediate_times.clear()

    logger.info(message, extra={SHOW_WHEN_ATTR: False, SHOW_WHERE_ATTR: False})
