"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import inspect as e
import pkgutil as pkgs
import sys as s
from pathlib import Path as path_t

from logger_36.constant.path import USER_FOLDER


def Modules(
    *,
    only_loaded: bool = True,
    with_version: bool = True,
    formatted: bool = False,
    indent: int = 0,
) -> tuple[str, ...] | str:
    """"""
    output = []

    if only_loaded:
        modules = s.modules
        module_names = set(modules.keys()).difference(s.stdlib_module_names)
        module_names = sorted(module_names, key=str.lower)
    else:
        modules = None
        module_names = _ModulesUsingPkgUtil()
    max_length = 0
    m_idx = 0
    for name in module_names:
        if name.startswith("_") or ("." in name):
            continue

        if with_version:
            if modules is None:
                version = "?"
            else:
                module = modules[name]
                # strip: Some packages have a \n at the end of their version. Just in
                # case, let's strip it left and right.
                version = getattr(module, "__version__", "?").strip()
            element = f"{name}={version}"
        else:
            element = name

        if formatted and (m_idx > 0) and (m_idx % 4 == 0):
            output.append("\n")
        output.append(element)

        if formatted:
            max_length = max(max_length, element.__len__())
            m_idx += 1

    if formatted:
        max_length += 4
        AlignedInColumns = lambda _: f"{_:{max_length}}" if _ != "\n" else "\n"
        output = map(AlignedInColumns, output)
        output = "".join(output).rstrip()

        spaces = indent * " "
        return spaces + f"\n{spaces}".join(map(str.rstrip, output.splitlines()))

    return tuple(output)


def _ModulesUsingPkgUtil() -> tuple[str, ...]:
    """
    Returns more results than using importlib.
    """
    return tuple(
        sorted(
            _elm.name
            for _elm in pkgs.iter_modules()
            if _elm.ispkg and (_elm.name[0] != "_") and ("__" not in _elm.name)
        )
    )


# import importlib.metadata as mprt
# def _ModulesUsingImportlib() -> tuple[str, ...]:
#     """"""
#     return tuple(
#         sorted(
#             _elm
#             for _elm in mprt.packages_distributions()
#             if (_elm[0] != "_") and ("__" not in _elm) and ("/" not in _elm)
#         )
#     )


def WhereInCode(
    *, should_be_formatted: bool = True, with_relative_path: bool = False
) -> str | tuple[path_t, str, int]:
    """"""
    frame = e.stack(context=0)[2][0]  # 2=caller of caller.
    details = e.getframeinfo(frame, context=0)
    path = path_t(details.filename)

    if should_be_formatted:
        if with_relative_path and path.is_relative_to(USER_FOLDER):
            path = path.relative_to(USER_FOLDER)
        return f"{str(path.with_suffix(''))}:{details.function}:{details.lineno}"

    return path, details.function, details.lineno
