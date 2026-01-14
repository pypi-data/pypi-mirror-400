"""
Class loggers_t for several loggers.

SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import logging as l
import typing as h

from logger_36.extension.data_class import NO_CHOICE
from logger_36.type.logger import logger_t


@d.dataclass(slots=True, repr=False, eq=False)
class loggers_t(dict[h.Hashable, logger_t]):
    """A dictionary that holds `logger_t` objects and an active logger.

    This class extends a standard dictionary to store logger instances identified by
    unique keys:
        dict[h.Hashable, logger_t]: A dictionary mapping unique identifiers
            (`h.Hashable`) to their corresponding `logger_t` instances.
    It also includes functionality to manage the current active logger.

    Attributes:
        active (logger_t | None): The currently active logger instance, if any.
    """
    active: logger_t | None = NO_CHOICE(None)

    def AddNew(
        self,
        uid: h.Hashable,
        /,
        *,
        name: str | None = None,
        level: int = l.NOTSET,
        exit_on_error: bool = False,
        exit_on_critical: bool = False,
        activate_wrn_interceptions: bool = True,
        activate_log_interceptions: bool = True,
        activate_exc_interceptions: bool = True,
    ) -> None:
        """Adds a new logger instance to the dictionary with the provided unique
        identifier (`uid`) and optional configuration parameters.

        Args:
            uid (h.Hashable): A unique identifier for the logger.
            name (str, optional): The logging handler's name. Defaults to `None`.
            level (int, optional): Sets the logging level. Defaults to `logging.NOTSET`.
            exit_on_error (bool, optional): Whether to call sys.exit(1) when an error
                occurs. Defaults to `False`.
            exit_on_critical (bool, optional): Whether to exit on a critical error.
                Defaults to `False`.
            activate_wrn_interceptions (bool, optional): Activates warning interception
                for this logger. Defaults to `True`.
            activate_log_interceptions (bool, optional): Activates log interception for
                this logger. Defaults to `True`.
            activate_exc_interceptions (bool, optional): Activates exception
                interception for this logger. Defaults to `True`.

        Raises:
            NameError: If a logger with the same identifier already exists in the
                dictionary.
        """
        logger = logger_t(
            exit_on_error=exit_on_error,
            exit_on_critical=exit_on_critical,
            name_=name,
            level_=level,
            activate_wrn_interceptions=activate_wrn_interceptions,
            activate_log_interceptions=activate_log_interceptions,
            activate_exc_interceptions=activate_exc_interceptions,
        )
        self.Add(uid, logger)

    def Add(self, uid: h.Hashable, logger: logger_t, /) -> None:
        """Adds a logger instance to the dictionary with the given unique identifier
        (`uid`).

        Args:
            uid (h.Hashable): A unique identifier for the logger.
            logger (logger_t): The logger instance to be added.

        Raises:
            NameError: If a logger with the same identifier already exists in the
                dictionary.
        """
        if uid in self:
            raise NameError(f"Logger with name/identity {uid} already exists.")

        self[uid] = logger
        self.active = logger

    def SetActive(self, uid: h.Hashable, /) -> None:
        """Sets a logger instance as active by its unique identifier (`uid`).

        Args:
            uid (h.Hashable): The unique identifier of the logger to set as active.
        """
        self.active = self[uid]
