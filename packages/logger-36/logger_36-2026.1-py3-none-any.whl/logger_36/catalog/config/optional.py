"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

try:
    import rich  # noqa
except ModuleNotFoundError:
    RICH_IS_AVAILABLE = False
    from logger_36.constant.error import MISSING_RICH_MESSAGE  # noqa
else:
    RICH_IS_AVAILABLE = True
    MISSING_RICH_MESSAGE = None

from logger_36.task.measure.memory import CanCheckUsage as CanCheckMemoryUsage

if CanCheckMemoryUsage():
    MEMORY_MEASURE_IS_AVAILABLE = True
    MEMORY_MEASURE_ERROR = None
else:
    MEMORY_MEASURE_IS_AVAILABLE = False
    from logger_36.constant.error import MEMORY_MEASURE_ERROR  # noqa
