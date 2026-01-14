"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import logging as l

TEXT_COLOR = "grey85"
WHERE_COLOR = "grey58"

LEVEL_COLOR = {
    l.DEBUG: "orchid",
    l.INFO: WHERE_COLOR,
    l.WARNING: "yellow1",
    l.ERROR: "dark_orange",
    l.CRITICAL: "bright_red",
}
ACTUAL_COLOR = LEVEL_COLOR[l.CRITICAL]
EXPECTED_COLOR = "green3"
RULE_COLOR = "sky_blue3"

ALTERNATIVE_BACKGROUND = (15, 15, 15)
