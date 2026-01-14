"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from datetime import datetime as date_time_t

from logger_36.config.message import DATE_FORMAT, TIME_FORMAT

# This module is imported early. Therefore, the current date and time should be close
# enough to the real start date and time of the main script.
START_DATE_TIME = date_time_t.now()

FORMATTED_START_DATE_TIME = f"{START_DATE_TIME:{TIME_FORMAT + ' on ' + DATE_FORMAT}}"

DATE_TIME_ORIGIN = date_time_t.fromtimestamp(1970, None)
DATE_ORIGIN = DATE_TIME_ORIGIN.date()
