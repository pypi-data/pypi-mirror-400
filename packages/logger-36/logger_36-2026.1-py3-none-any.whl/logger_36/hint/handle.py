"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import logging as l
import typing as h

logger_handle_raw_h = h.Callable[[l.LogRecord], None]
logger_handle_with_self_h = h.Callable[[l.Logger, l.LogRecord], None]
logger_handle_h = logger_handle_raw_h | logger_handle_with_self_h
