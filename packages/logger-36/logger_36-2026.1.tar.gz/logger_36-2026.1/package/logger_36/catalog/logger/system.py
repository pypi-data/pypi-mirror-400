"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from logger_36.constant.system import MAX_DETAIL_NAME_LENGTH, SYSTEM_DETAILS_AS_DICT
from logger_36.extension.inspection import Modules
from logger_36.instance.logger import L
from logger_36.type.logger import logger_t


def LogSystemDetails(
    *,
    should_restrict_modules_to_loaded: bool = True,
    modules_with_version: bool = True,
    modules_formatted: bool = True,
    indent: int = 4,
    logger: logger_t = L,
) -> None:
    """"""
    details = "\n".join(
        f"    {_key:>{MAX_DETAIL_NAME_LENGTH}}: {_vle}"
        for _key, _vle in SYSTEM_DETAILS_AS_DICT.items()
    )
    modules = Modules(
        only_loaded=should_restrict_modules_to_loaded,
        with_version=modules_with_version,
        formatted=modules_formatted,
        indent=indent,
    )

    logger.info(
        f"SYSTEM DETAILS\n"
        f"{details}\n"
        f"    {'Python Modules':>{MAX_DETAIL_NAME_LENGTH}}:\n"
        f"{modules}"
    )
