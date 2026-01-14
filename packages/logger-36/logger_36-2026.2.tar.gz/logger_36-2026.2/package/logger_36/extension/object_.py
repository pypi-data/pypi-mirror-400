"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import inspect as e
import typing as h
from collections import abc
from multiprocessing.shared_memory import SharedMemory as shared_memory_t

_ROOT_NAME = "TOTAL"
_INDENTATION = "    "


def ObjectSize(
    obj: h.Any, /, *, should_return_details: bool = False, lock=None
) -> int | tuple[int, dict[str, h.Any] | None]:
    """"""
    already_sized = []
    if should_return_details:
        hierarchy = {}
    else:
        hierarchy = None

    size = _ObjectSize(obj, already_sized, _ROOT_NAME, hierarchy, lock)

    if hierarchy is None:
        return size

    _, hierarchy = hierarchy.popitem()
    if isinstance(hierarchy, dict):
        return size, hierarchy
    return size, None


def _ObjectSize(
    obj: h.Any,
    already_sized: list[int],
    current: str,
    hierarchy: dict[str, h.Any] | None,
    lock,
    /,
) -> int:
    """"""
    current = f"{current}:{type(obj).__name__}"

    uid = id(obj)
    if uid in already_sized:
        if hierarchy is not None:
            hierarchy[current] = 0
        return 0

    already_sized.append(uid)

    SizeOf = getattr(obj, "__sizeof__", None)
    if SizeOf is None:  # Probably unlikely.
        if hierarchy is not None:
            hierarchy[current] = -1
        return 0

    try:
        output = SizeOf()
    except Exception:  # For example, float.__sizeof__() => TypeError.
        if hierarchy is not None:
            hierarchy[current] = -1
        return 0

    if not e.isbuiltin(SizeOf):
        # The __sizeof__ method has been overridden; Its output should be trusted.
        if hierarchy is not None:
            hierarchy[current] = output
        return output

    # Deal with buffer-like objects to avoid iterating over their items; First shared
    # memory...
    if isinstance(obj, shared_memory_t):
        if lock is None:
            if hierarchy is not None:
                hierarchy[current] = -1
            return output
        with lock:
            total = output + obj.size
            if hierarchy is not None:
                hierarchy[current] = total
            return total

    # ... Then objects following the buffer protocol.
    try:
        view = memoryview(obj)
    except Exception:
        pass
    else:
        view.release()
        if hierarchy is not None:
            hierarchy[current] = output
        return output

    # Deal with mappings before iterables since mappings can also be iterated over. They
    # are not sequences though, but just in case, keep mappings first.
    if isinstance(obj, abc.Mapping):
        if obj.__len__() > 0:
            if hierarchy is None:
                subhierarchy = None
            else:
                subhierarchy = {}
            output += sum(
                _ObjectSize(_, already_sized, f"KEY_{_}", subhierarchy, lock)
                + _ObjectSize(__, already_sized, f"VALUE_{_}", subhierarchy, lock)
                for _, __ in obj.items()
            )
            if hierarchy is not None:
                hierarchy[f"{current} = {output}"] = subhierarchy
        elif hierarchy is not None:
            hierarchy[current] = output

        return output

    if isinstance(obj, abc.Sequence) and not isinstance(obj, str):
        if obj.__len__() > 0:
            if hierarchy is None:
                subhierarchy = None
            else:
                subhierarchy = {}
            output += sum(
                _ObjectSize(__, already_sized, f"[{_}]", subhierarchy, lock)
                for _, __ in enumerate(obj)
            )
            if hierarchy is not None:
                hierarchy[f"{current} = {output}"] = subhierarchy
        elif hierarchy is not None:
            hierarchy[current] = output

        return output

    # Note: There can be both slots and a dictionary.
    slots = getattr(obj.__class__, "__slots__", None)
    has_slots = slots is not None

    if (attributes := getattr(obj, "__dict__", None)) is not None:
        if attributes.__len__() > 0:
            if hierarchy is None:
                subhierarchy = None
            else:
                subhierarchy = {}
            output += sum(
                _ObjectSize(__, already_sized, _, subhierarchy, lock)
                for _, __ in attributes.items()
            )
            if hierarchy is not None:
                hierarchy[f"{current} = {output}"] = subhierarchy
        elif not (has_slots or (hierarchy is None)):
            hierarchy[current] = output

        if not has_slots:
            return output

    if has_slots:
        if isinstance(slots, str):
            slots = (slots,)
        else:
            slots = tuple(slots)
        if slots.__len__() > 0:
            if hierarchy is None:
                subhierarchy = None
            else:
                subhierarchy = {}
            output += sum(
                _ObjectSize(getattr(obj, _), already_sized, _, subhierarchy, lock)
                for _ in slots
            )
            if hierarchy is not None:
                hierarchy[f"{current} = {output}"] = subhierarchy
        elif hierarchy is not None:
            hierarchy[current] = output

        return output

    if hierarchy is not None:
        hierarchy[current] = output

    return output


def FormattedObjectSizeHierarchy(hierarchy: dict[str, h.Any], /) -> str:
    """"""
    return "\n".join(_FormattedObjectSizeHierarchy(hierarchy, 0))


def _FormattedObjectSizeHierarchy(
    hierarchy: dict[str, h.Any], level: int, /
) -> list[str]:
    """"""
    output = []

    indentation = level * _INDENTATION
    for key, value in hierarchy.items():
        if isinstance(value, dict):
            output.append(f"{indentation}{key}")
            output.extend(_FormattedObjectSizeHierarchy(value, level + 1))
        else:
            output.append(f"{indentation}{key} = {value}")

    return output
