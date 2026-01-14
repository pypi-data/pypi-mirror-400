"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import multiprocessing as prll

from logger_36.constant.logger import LOGGER_NAME
from logger_36.constant.system import MAIN_PROCESS_NAME
from logger_36.type.logger import logger_t
from mpss_tools_36.api.sharer import proxy_t

if prll.current_process().name == MAIN_PROCESS_NAME:
    L = logger_t(name_=LOGGER_NAME, _is_singleton=True)
else:
    L = proxy_t.SharedInstanceProxy(LOGGER_NAME)
