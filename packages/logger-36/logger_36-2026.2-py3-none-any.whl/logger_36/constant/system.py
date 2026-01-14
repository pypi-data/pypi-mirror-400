"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import platform as pltf

from logger_36.config.system import SYSTEM_DETAILS

SYSTEM_DETAILS_AS_DICT = {_.capitalize(): getattr(pltf, _)() for _ in SYSTEM_DETAILS}
MAX_DETAIL_NAME_LENGTH = max(map(len, SYSTEM_DETAILS_AS_DICT.keys()))

MAIN_PROCESS_NAME = "MainProcess"
UNKNOWN_PROCESS_NAME = "<UNKNOWN_PROCESS_NAME>"
