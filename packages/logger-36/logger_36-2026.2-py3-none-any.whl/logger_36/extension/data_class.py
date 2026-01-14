"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h


def NO_CHOICE(default: h.Any | h.Callable[[], h.Any], /) -> h.Any:
    """
    Use constant letter casing because they are supposed to be constants. Unfortunately,
    dataclasses.field's cannot be shared across attributes.
    """
    if isinstance(default, h.Callable):
        return d.field(init=False, default_factory=default)
    return d.field(init=False, default=default)
