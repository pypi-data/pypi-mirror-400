"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import re as r

LOGGER_NAME = "logger-36 default"

# https://docs.python.org/3/library/logging.html#logging.captureWarnings
WARNING_LOGGER_NAME = "py.warnings"
WARNING_TYPE_PATTERN = r"\s*([^:]+):([0-9]+):\s*([^:]+)\s*:((.|\n)*)"
WARNING_TYPE_COMPILED_PATTERN = r.compile(WARNING_TYPE_PATTERN)
