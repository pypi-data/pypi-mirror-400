"""
Logging handler classes non_file_handler_t, file_handler_t, and extension_t.

SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import logging as l
import tempfile as tmps
import typing as h
from pathlib import Path as path_t

from logger_36.config.message import FALLBACK_MESSAGE_WIDTH
from logger_36.config.rule import DEFAULT_RULE_LENGTH, RULE_CHARACTER
from logger_36.constant.message import (
    NEXT_LINE_PROLOGUE,
    PROCESS_PROLOGUE,
    TIME_PLACEHOLDER,
    WHERE_PROLOGUE,
)
from logger_36.constant.record import (
    HAS_ACTUAL_EXPECTED_ATTR,
    PROCESS_NAME_ATTR,
    RULE_COLOR_ATTR,
    SHOW_W_RULE_ATTR,
    WHEN_OR_ELAPSED_ATTR,
    WHERE_ATTR,
)
from logger_36.constant.rule import DEFAULT_RULE, MIN_HALF_RULE_LENGTH
from logger_36.constant.system import MAIN_PROCESS_NAME, UNKNOWN_PROCESS_NAME
from logger_36.extension.text import WrappedLines
from logger_36.hint.record import layout_h, records_h
from logger_36.type.theme import theme_t


class extension_t:
    """
    A base extension class for logger handlers providing message formatting and rule generation.

    This class serves as a foundation for custom logger extensions, handling message
    formatting, text wrapping, rule generation, and theme application for log records.

    Attributes:
        name (str | None): Identifier for the extension instance.
        message_width (int): Maximum width for message wrapping; <=0 disables wrapping.
        theme (str | theme_t | None): Theme configuration for colorized output.
        _wrapping_is_disabled (bool): Internal flag indicating if message wrapping is disabled.
    """

    def __init__(
        self, name: str | None, message_width: int, theme: str | theme_t | None, /
    ) -> None:
        """
        Initialize the extension with configuration parameters.

        Args:
            name (str | None): Extension identifier. If None, auto-generated.
            message_width (int): Maximum width for message wrapping.
                Values <= 0 disable wrapping entirely.
            theme (str | theme_t | None): Theme for colorized output.
                String values are converted to theme_t instances.

        Note:
            Uses positional-only parameters (indicated by /).
        """
        self.name = name
        self.message_width = message_width
        self._wrapping_is_disabled = True
        self.theme = theme

        self.__post_init__()

    def __post_init__(self) -> None:
        """
        Post-initialization setup and validation.

        Performs:
        - Auto-generates name if None
        - Validates and adjusts message_width against FALLBACK_MESSAGE_WIDTH
        - Sets wrapping disabled flag based on message_width
        - Converts string themes to theme_t instances
        """
        if self.name is None:
            self.name = f"{type(self).__name__}:{hex(id(self))[2:]}"

        if 0 < self.message_width < FALLBACK_MESSAGE_WIDTH:
            self.message_width = FALLBACK_MESSAGE_WIDTH
        self._wrapping_is_disabled = self.message_width <= 0

        if isinstance(self.theme, str):
            self.theme = theme_t.NewDefaultFromStr(self.theme)

    @property
    def records(self) -> tuple[records_h | None, layout_h | None]:
        """
        Get records and layout information for the extension.

        Returns:
            tuple[records_h | None, layout_h | None]:
                A tuple containing records and layout objects, or (None, None) by default.
        """
        return None, None

    @classmethod
    def New(cls, **kwargs) -> h.Self:
        """
        Create a new instance with flexible keyword arguments.

        This class method provides a factory interface with default arguments,
        no prescribed argument order, and variable argument list support.

        Args:
            **kwargs: Arbitrary keyword arguments for instance configuration.

        Returns:
            h.Self: A new instance of the class.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def MessageFromRecord(self, record: l.LogRecord, /) -> str | h.Any:
        """
        Format a log message from a LogRecord with optional styling and wrapping.

        Processes the log record to create a formatted message with:
        - Rule-based formatting (if SHOW_W_RULE_ATTR is set)
        - Message wrapping and indentation (if enabled)
        - Timestamp, level, process, and location information
        - Theme-based colorization (if theme is configured)

        Args:
            record (l.LogRecord): The log record to format. Uses positional-only parameter.

        Returns:
            str | h.Any: Formatted message string or theme-specific object (e.g., for Rich).

        Note:
            Message can be None in the record. Multi-line messages are handled with
            proper indentation using NEXT_LINE_PROLOGUE.
        """
        message = record.msg  # See logger_36.catalog.handler.README.txt.

        # Here, message can be None.
        if getattr(record, SHOW_W_RULE_ATTR, False):
            color = getattr(record, RULE_COLOR_ATTR, None)
            return self.Rule(text=message, color=color)
        # Here, message is supposed to be an str.

        # Indent message (if multi-line) and wrap it (if requested).
        if self._wrapping_is_disabled or (message.__len__() <= self.message_width):
            if "\n" in message:
                message = message.replace("\n", NEXT_LINE_PROLOGUE)
        else:
            if "\n" in message:
                lines = message.splitlines()
            else:
                lines = [message]
            message = NEXT_LINE_PROLOGUE.join(WrappedLines(lines, self.message_width))

        when_or_elapsed = getattr(record, WHEN_OR_ELAPSED_ATTR, TIME_PLACEHOLDER)
        if (where := getattr(record, WHERE_ATTR, None)) is None:
            where = ""
        else:
            where = f"{WHERE_PROLOGUE}{where}"
        process_name = getattr(
            record,
            PROCESS_NAME_ATTR,
            getattr(record, "processName", UNKNOWN_PROCESS_NAME),
        )
        # PROCESS_NAME_ATTR: A workaround to pass the process name for forkserver and
        # spawn start methods, since in these cases, the actual logging is done by the
        # sharing server from the main process, and processName cannot be overwritten:
        #     KeyError: "Attempt to overwrite 'processName' in LogRecord"
        if process_name != MAIN_PROCESS_NAME:
            process_name = f"{PROCESS_PROLOGUE}{process_name}"
        else:
            process_name = ""

        if self.theme is None:
            return (
                f"{when_or_elapsed}_{record.levelname[0].lower()} {message}"
                f"{where}{process_name}"
            )

        return self.theme.ColorizedMessage(
            record.levelno,
            f"{when_or_elapsed}_{record.levelname[0].lower()} ",
            message,
            f"{where}{process_name}",
            getattr(record, HAS_ACTUAL_EXPECTED_ATTR, False),
        )

    def Rule(
        self, /, *, text: str | None = None, color: str | None = None
    ) -> str | h.Any:
        """
        Generate a rule line with optional centered text.

        Creates horizontal rules using RULE_CHARACTER. If text is provided,
        centers it within the rule. Returns h.Any type hint to support
        Rich and other styling libraries.

        Args:
            text (str | None, optional): Text to center within the rule.
                If None, creates a solid rule line. Defaults to None.
            color (str | None, optional): Color specification for the rule.
                Defaults to None.

        Returns:
            str | h.Any: Rule string or styled object for libraries like Rich.

        Examples:
            >>> ext = extension_t()
            >>> ext.Rule()
            "=========================================="
            >>> ext.Rule(text="SECTION")
            "================== SECTION =================="
        """
        if text is None:
            if self.message_width > 0:
                return self.message_width * RULE_CHARACTER
            return DEFAULT_RULE

        if self.message_width > 0:
            target_width = self.message_width
        else:
            target_width = DEFAULT_RULE_LENGTH
        half_rule_length = max(
            (target_width - text.__len__() - 2) // 2, MIN_HALF_RULE_LENGTH
        )
        half_rule = half_rule_length * RULE_CHARACTER

        return f"{half_rule} {text} {half_rule}"


class non_file_handler_t(l.Handler, extension_t):
    """
    A non-file based logger handler with extension capabilities.

    Combines Python's standard logging Handler with extension_t functionality
    for enhanced message formatting in non-file outputs (console, stream, etc.).

    Inherits from:
        l.Handler: Standard Python logging handler base class
        extension_t: Enhanced formatting and theming capabilities
    """

    def __init__(
        self,
        name: str | None,
        message_width: int,
        level: int,
        theme: str | theme_t | None,
        *_,
    ) -> None:
        """
        Initialize the non-file handler with formatting and level configuration.

        Args:
            name (str | None): Handler identifier.
            message_width (int): Maximum message width for wrapping.
            level (int): Logging level threshold.
            theme (str | theme_t | None): Theme for colorized output.
            *_ : Additional positional arguments (ignored).

        Note:
            Uses positional-only parameters for first four arguments.
        """
        l.Handler.__init__(self)
        extension_t.__init__(self, name, message_width, theme)
        __post_init__(self, level)


class file_handler_t(l.FileHandler, extension_t):
    """
    A file-based logger handler with extension capabilities.

    Extends Python's FileHandler with enhanced formatting from extension_t
    for file-based logging with advanced message formatting.

    Inherits from:
        l.FileHandler: Standard Python file handler
        extension_t: Enhanced formatting capabilities
    """

    def __init__(
        self,
        name: str | None,
        message_width: int,
        level: int,
        path: str | path_t | None,
        *_,
    ) -> None:
        """
        Initialize the file handler with path validation and configuration.

        Args:
            name (str | None): Handler identifier.
            message_width (int): Maximum message width for wrapping.
            level (int): Logging level threshold.
            path (str | path_t | None): File path for logging output.
            *_ : Additional positional arguments (ignored).

        Raises:
            ValueError: If path is None, or if path exists and is not in temp directory.

        Note:
            Automatically converts string paths to path_t objects.
            Prevents overwriting existing files outside temp directory for safety.
        """
        if path is None:
            raise ValueError("Missing file or folder.")
        if isinstance(path, str):
            path = path_t(path)
        if path.exists() and not path.is_relative_to(tmps.gettempdir()):
            raise ValueError(f"File or folder already exists: {path}.")

        l.FileHandler.__init__(self, path)
        extension_t.__init__(self, name, message_width, None)
        __post_init__(self, level)


handler_h = non_file_handler_t | file_handler_t


def __post_init__(handler: handler_h, level: int) -> None:
    """
    Perform post-initialization setup for handler instances.

    Sets the logging level on the handler after initialization.

    Args:
        handler (handler_h): The handler instance to configure.
        level (int): Logging level to set on the handler.
    """
    handler.setLevel(level)
