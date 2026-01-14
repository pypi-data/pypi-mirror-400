"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import os as o
import tempfile as tmps
from pathlib import Path as path_t


def NewUniqueName(existing: path_t, /) -> path_t:
    """"""
    folder, name, extension = existing.parent, existing.stem, existing.suffix

    version = 1
    while (folder / f"{name}-{version}{extension}").exists():
        version += 1

    return folder / f"{name}-{version}{extension}"


def NewTemporaryFile(
    suffix: str, /, *, should_return_accessor: bool = False
) -> path_t | tuple[path_t, int]:
    """"""
    accessor, path = tmps.mkstemp(suffix=suffix)
    path = path_t(path)

    if should_return_accessor:
        return path, accessor

    o.close(accessor)
    return path
