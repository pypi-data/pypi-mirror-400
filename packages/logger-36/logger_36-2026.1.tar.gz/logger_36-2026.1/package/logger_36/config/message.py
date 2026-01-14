"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import re as r
from datetime import timedelta as time_delta_t

WHERE_SEPARATOR = "@"
PROCESS_SEPARATOR = "↖"
ELAPSED_TIME_SEPARATOR = "+"
FALLBACK_MESSAGE_WIDTH = 20

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
LONG_ENOUGH = time_delta_t(minutes=5)

ACTUAL_PATTERN = r" Actual="
ACTUAL_PATTERN_COMPILED = r.compile(ACTUAL_PATTERN)
ACTUAL_PATTERNS = (ACTUAL_PATTERN,)
EXPECTED_PATTERN = r" Expected([!<>]?=|: )"
EXPECTED_PATTERN_COMPILED = r.compile(EXPECTED_PATTERN)
