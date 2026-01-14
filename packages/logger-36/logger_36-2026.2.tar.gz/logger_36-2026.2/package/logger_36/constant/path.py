"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import inspect as e
import tempfile as tmps
from pathlib import Path as path_t

USER_FOLDER = path_t.home()

_frame = e.stack(context=0)[-1]  # -1=root caller.
if path_t(_frame.filename).exists():
    LAUNCH_ROOT_FILE = path_t(_frame.filename)
    LAUNCH_FOLDER = LAUNCH_ROOT_FILE.parent

    if LAUNCH_ROOT_FILE.is_relative_to(USER_FOLDER):
        LAUNCH_ROOT_FILE_relative = LAUNCH_ROOT_FILE.relative_to(USER_FOLDER)
    else:
        LAUNCH_ROOT_FILE_relative = LAUNCH_ROOT_FILE
else:
    LAUNCH_ROOT_FILE = LAUNCH_ROOT_FILE_relative = "<unknown launch root file>"
    LAUNCH_FOLDER = path_t(tmps.mkdtemp())
