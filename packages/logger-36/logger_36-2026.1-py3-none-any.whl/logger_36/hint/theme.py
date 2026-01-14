"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

layout_h = h.Literal["html", "rich"]
for_background_h = h.Literal["dark", "light"]
type color_h = (
    str
    | tuple[int | float, int | float, int | float]
    | tuple[int | float, int | float, int | float, int | float]
)
# Parameters: h.Any=theme_t, log_level, when_or_elapsed_and_level, message,
#     where_and_process, has_actual_expected.
colorized_message_fct_h = h.Callable[[h.Any, int, str, str, str, bool], h.Any]
