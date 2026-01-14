"""
Logger class logger_t.

SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import logging as l
import multiprocessing as prll
import shutil as shll
import sys as s
import threading as thrd
import traceback as tcbk
import types as t
import typing as h
from datetime import date as date_t
from datetime import datetime as date_time_t
from pathlib import Path as path_t
from pickle import dumps as PickleStringOf
from traceback import TracebackException as traceback_t

from logger_36.catalog.config.optional import (
    MEMORY_MEASURE_ERROR,
    MEMORY_MEASURE_IS_AVAILABLE,
    MISSING_RICH_MESSAGE,
    RICH_IS_AVAILABLE,
)
from logger_36.catalog.handler.console import console_handler_t
from logger_36.catalog.handler.file import file_handler_t
from logger_36.config.issue import ISSUE_CONTEXT_END, ISSUE_CONTEXT_SEPARATOR
from logger_36.config.message import (
    DATE_FORMAT,
    LONG_ENOUGH,
    TIME_FORMAT,
    WHERE_SEPARATOR,
)
from logger_36.constant.chronos import DATE_ORIGIN, DATE_TIME_ORIGIN
from logger_36.constant.issue import ISSUE_LEVEL_SEPARATOR
from logger_36.constant.logger import WARNING_LOGGER_NAME
from logger_36.constant.memory import UNKNOWN_MEMORY_USAGE
from logger_36.constant.message import LINE_BREAK_AND_SPACE
from logger_36.constant.path import LAUNCH_ROOT_FILE_relative
from logger_36.constant.record import (
    HAS_ACTUAL_EXPECTED_ATTR,
    PROCESS_NAME_ATTR,
    RULE_COLOR_ATTR,
    SHOW_W_RULE_ATTR,
    SHOW_WHEN_ATTR,
    SHOW_WHERE_ATTR,
    WHEN_OR_ELAPSED_ATTR,
    WHERE_ATTR,
)
from logger_36.constant.system import MAIN_PROCESS_NAME, UNKNOWN_PROCESS_NAME
from logger_36.extension.data_class import NO_CHOICE
from logger_36.extension.file import NewTemporaryFile, NewUniqueName
from logger_36.extension.inspection import WhereInCode
from logger_36.extension.sentinel import NOT_PASSED
from logger_36.hint.handle import logger_handle_h
from logger_36.hint.issue import order_h
from logger_36.hint.message import expected_op_h
from logger_36.hint.record import IsRecordsAndLayout, records_h
from logger_36.hint.record import layout_h as record_layout_h
from logger_36.hint.value import layout_h as value_layout_h
from logger_36.task.format.chronos import FormattedElapsedTime
from logger_36.task.format.message import MessageWithActualExpected
from logger_36.task.interception import HandleForInterceptions, HandleForWarnings
from logger_36.task.measure.chronos import TimeStamp
from logger_36.task.measure.memory import CurrentUsage as CurrentMemoryUsage
from logger_36.type.handler import handler_h as base_handler_h
from logger_36.type.issue import NewIssue, issue_t
from logger_36.type.theme import theme_t
from mpss_tools_36.api.sharer import server_t
from mpss_tools_36.api.sharer_singleton import ToggleShareability

if RICH_IS_AVAILABLE:
    from logger_36.catalog.handler.console_rich import console_rich_handler_t
else:
    from logger_36.catalog.handler.console import (
        console_handler_t as console_rich_handler_t,
    )

base_t = l.Logger


@d.dataclass(slots=True, repr=False, eq=False)
class logger_t(base_t):
    """
    Advanced logging class with extended functionality beyond standard Python logging.

    This logger provides enhanced features including:
    - Automatic interception of warnings, logs from other loggers, and exceptions
    - Memory usage monitoring and tracking
    - Message holding/buffering capabilities
    - Multiprocess safety with queue-based handling
    - Context-aware issue staging and batch commit
    - File and value logging to disk
    - Rich terminal output support (when available)
    - Automatic timestamping and location tracking

    The logger extends Python's standard logging.Logger with dataclass functionality,
    providing a clean interface for configuration and state management.

    Attributes:
        exit_on_error (bool): If True, calls sys.exit(1) on ERROR level messages.
            Also implies exit_on_critical=True. Defaults to False.
        exit_on_critical (bool): If True, calls sys.exit(1) on CRITICAL level messages.
            Defaults to False.
        should_monitor_memory_usage (bool): If True, tracks memory usage at each log
            call and records it in memory_usages. Defaults to False.
        should_hold_messages (bool | Any): If True, log records are queued in on_hold
            instead of being immediately processed. In multiprocess mode, this becomes
            a multiprocessing.Value. Defaults to False.
        folder (path_t | str | None): Base directory for storing log outputs and files.
            If provided, a timestamped subfolder is created. Defaults to None.
        _is_singleton (bool): Will the logger be the global instance logger_36.L? For
            internal use only. Defaults to False.
        time_stamp (str): String timestamp of logger creation, used for folder naming
            and identification. Auto-generated at initialization.
        on_hold (list[l.LogRecord] | Any): Queue/list of log records waiting to be
            processed when should_hold_messages is True. In multiprocess mode, becomes
            a multiprocessing.Queue.
        history (dict[date_time_t, str]): Timeline of significant logger events
            (handler additions, interception toggles, etc.) with timestamps.
        intermediate_times (list[tuple[str, str, date_time_t]] | Any): Named checkpoints
            with format (name, process_name, timestamp). In multiprocess mode, becomes
            a managed list.
        memory_usages (list[tuple[str, str, int, int]] | Any): Memory measurements with
            format (location, process_name, current_usage, total_usage). In multiprocess
            mode, becomes a managed list.
        pid (int): Process ID of the main process that created this logger.
        last_message_now (date_time_t): Timestamp of the most recent log message.
        last_message_date (date_t): Date of the most recent log message. Used to
            automatically insert date separators.
        context_levels (list[str]): Stack of context strings for nested operations.
            Used with staged issues and context managers.
        staged_issues (list[tuple[issue_t, bool]]): Accumulated issues waiting to be
            committed in batch. Each tuple contains (issue_message, has_actual_expected).
        intercepted_wrn_handle (logger_handle_h | None): Original handle method of the
            Python warnings logger, stored when interception is enabled. This allows
            warnings to be restored later.
        intercepted_log_handles (dict[str, logger_handle_h]): Original handle methods
            of other loggers being intercepted, keyed by logger name.
        intercepts_exceptions (bool): Whether sys.excepthook and threading.excepthook
            have been replaced to route exceptions through this logger.
        _should_activate_log_interceptions (bool): Internal flag indicating log
            interception should be activated on first handler addition.
        server (server_t | None): Sharing server to access the logger in the main
            process in multiprocess mode.
        proxy: The logger proxy created as a not-really-sharing workaround for the
            global instance logger_36.instance.L when the multiprocessing start method
            is "fork". See logger_t.ToggleShareability.

    Note:
        This logger MUST be instantiated from the main process. Multiprocess safety
        features will fail if initialized from a child process.

        _should_activate_log_interceptions exists because loggers instantiated after this
        logger_t would be missed by an early ToggleLogInterceptions call. Setting
        activate_log_interceptions=True only sets this flag, which is checked in
        AddHandler to effectively call ToggleLogInterceptions at the right time.
    """

    exit_on_error: bool = False
    exit_on_critical: bool = False
    should_monitor_memory_usage: bool = False
    should_hold_messages: bool | h.Any = False
    folder: path_t | str | None = None
    _is_singleton: bool = False

    time_stamp: str = NO_CHOICE(TimeStamp)
    on_hold: list[l.LogRecord] | h.Any = NO_CHOICE(list)
    history: dict[date_time_t, str] = NO_CHOICE(dict)
    intermediate_times: list[tuple[str, str, date_time_t]] | h.Any = NO_CHOICE(list)
    memory_usages: list[tuple[str, str, int, int]] | h.Any = NO_CHOICE(list)

    pid: int = d.field(init=False)
    last_message_now: date_time_t = NO_CHOICE(DATE_TIME_ORIGIN)
    last_message_date: date_t = NO_CHOICE(DATE_ORIGIN)
    context_levels: list[str] = NO_CHOICE(list)
    staged_issues: list[tuple[issue_t, bool]] = NO_CHOICE(list)
    intercepted_wrn_handle: logger_handle_h | None = NO_CHOICE(None)
    intercepted_log_handles: dict[str, logger_handle_h] = NO_CHOICE(dict)
    intercepts_exceptions: bool = NO_CHOICE(False)

    _should_activate_log_interceptions: bool = NO_CHOICE(False)

    server: server_t | None = NO_CHOICE(None)
    proxy: h.Any | None = NO_CHOICE(None)

    name_: d.InitVar[str | None] = None
    level_: d.InitVar[int] = l.NOTSET
    activate_wrn_interceptions: d.InitVar[bool] = True
    activate_log_interceptions: d.InitVar[bool] = True
    activate_exc_interceptions: d.InitVar[bool] = True

    @property
    def formatted_history(self) -> str:
        """
        Get a human-readable formatted string of the logger's history.

        Returns:
            str: Multi-line string with each history entry formatted as
                "timestamp: message". Line breaks within messages are replaced
                with "\\n " for readability.

        Example:
            >>> from logger_36 import L
            >>> L.formatted_history
            "2025-10-17 10:30:15: Logger instantiation\\n2025-10-17 10:30:16: New handler added"
        """
        FormattedEntry = lambda _: f"{_[0]}: {_[1].replace('\n', LINE_BREAK_AND_SPACE)}"
        return "\n".join(map(FormattedEntry, self.history.items()))

    @property
    def records(self) -> tuple[records_h | None, record_layout_h | None]:
        """See logger_t.Records"""
        return logger_t.Records(self)

    @staticmethod
    def Records(
        logger: base_t | l.Logger, /
    ) -> tuple[records_h | None, record_layout_h | None]:
        """
        Get the records and layout from the first handler that provides them.

        Searches through all attached handlers for one that has a 'records' attribute
        containing both records data and layout information.

        Args:
            logger (base_t | l.Logger): The logger instance to inspect for records.

        Returns:
            tuple[records_h | None, record_layout_h | None]: A tuple containing:
                - records: Collection of log records if any handler provides them
                - layout: Layout specification if any handler provides it
                - (None, None) if no handler provides records

        Note:
            This static method allows extracting records from any logger, not just
            logger_t instances.
        """
        for handler in logger.handlers:
            output = getattr(handler, "records", None)
            if IsRecordsAndLayout(output):
                return output

        return None, None

    @property
    def intercepts_warnings(self) -> bool:
        """
        Check if warning interception is currently active.

        Returns:
            bool: True if Python warnings are being intercepted and routed through
                this logger, False otherwise.
        """
        return self.intercepted_wrn_handle is not None

    @property
    def intercepts_logs(self) -> bool:
        """
        Check if log interception from other loggers is currently active.

        Returns:
            bool: True if other loggers' outputs are being intercepted, False otherwise.
        """
        return self.intercepted_log_handles.__len__() > 0

    @property
    def has_staged_issues(self) -> bool:
        """
        Check if there are any staged issues waiting to be committed.

        Returns:
            bool: True if staged_issues is non-empty, False otherwise.
        """
        return self.staged_issues.__len__() > 0

    @property
    def n_staged_issues(self) -> int:
        """
        Get the count of currently staged issues.

        Returns:
            int: Number of issues in the staged_issues list.
        """
        return self.staged_issues.__len__()

    @property
    def max_memory_usage(self) -> int:
        """
        Get the maximum total memory usage recorded across all measurements.

        Returns:
            int: Maximum memory usage in bytes, or UNKNOWN_MEMORY_USAGE if no
                measurements have been recorded.

        Note:
            This only includes measurements taken when should_monitor_memory_usage
            is enabled.
        """
        if self.memory_usages.__len__() > 0:
            return max(_[-1] for _ in self.memory_usages)
        return UNKNOWN_MEMORY_USAGE

    @property
    def max_memory_usage_full(self) -> tuple[str, str, int, int]:
        """
        Get full details of the measurement with maximum memory usage.

        Returns:
            tuple[str, str, int, int]: A tuple containing:
                - location (str): Code location where max usage was recorded
                - process_name (str): Name of the process
                - current_usage (int): Process-specific memory usage in bytes
                - total_usage (int): Total system memory usage in bytes

                Returns ("?", "?", UNKNOWN_MEMORY_USAGE, UNKNOWN_MEMORY_USAGE) if
                no measurements exist.

        Example:
            >>> from logger_36 as L
            >>> location, process, current, total = L.max_memory_usage_full
            >>> print(f"Max memory at {location}: {total} bytes")
        """
        if self.memory_usages.__len__() > 0:
            where_s, processes, usages, totals = zip(*self.memory_usages)

            max_usage = max(totals)
            max_idx = totals.index(max_usage)

            return where_s[max_idx], processes[max_idx], usages[max_idx], max_usage

        return "?", "?", UNKNOWN_MEMORY_USAGE, UNKNOWN_MEMORY_USAGE

    def __post_init__(
        self,
        name_: str | None,
        level_: int,
        activate_wrn_interceptions: bool,
        activate_log_interceptions: bool,
        activate_exc_interceptions: bool,
    ) -> None:
        """
        Initialize the logger after dataclass field initialization.

        This method is automatically called after __init__ due to dataclass mechanics.
        It sets up the logger's base functionality, folder structure, and optional
        interceptions.

        Args:
            name_ (str | None): Logger name. If None, generates a unique name based
                on the class type and instance id.
            level_ (int): Logging level threshold (e.g., logging.DEBUG, logging.INFO).
            activate_wrn_interceptions (bool): If True, immediately activates Python
                warning interception.
            activate_log_interceptions (bool): If True, marks log interception for
                activation when the first handler is added.
            activate_exc_interceptions (bool): If True, immediately activates exception
                interception via sys.excepthook.

        Raises:
            AssertionError: If called from a process other than the main process.

        Note:
            This method enforces that the logger must be instantiated in the main
            process to ensure proper functioning of multiprocess features.
        """
        process = prll.current_process()
        assert process.name == MAIN_PROCESS_NAME

        if name_ is None:
            name_ = f"{type(self).__name__}:{hex(id(self))[2:]}"

        self.SetFolder(self.folder)
        self.pid = process.pid
        self._AddHistoricalEvent(
            f'Logger "{name_}" instantiation for "{LAUNCH_ROOT_FILE_relative}"'
        )

        base_t.__init__(self, name_)
        self.setLevel(level_)
        self.propagate = False  # Part of base_t.

        if self.exit_on_error:
            self.exit_on_critical = True

        if activate_wrn_interceptions:
            self.ToggleWarningInterceptions(True)
        if activate_log_interceptions:
            self._should_activate_log_interceptions = True
        if activate_exc_interceptions:
            self.ToggleExceptionInterceptions(True)

        if self.should_monitor_memory_usage:
            self.ActivateMemoryUsageMonitoring()

    def SetFolder(self, folder: path_t | str | None, /) -> None:
        """
        Configure the base folder for storing log-related files.

        Creates a timestamped subfolder within the specified folder. If a folder
        with the timestamp already exists, appends a version number.

        Args:
            folder (path_t | str | None): Base folder path. Can be:
                - None: No folder is set (temporary files will be used as needed)
                - str: Converted to Path object
                - Path: Used directly

        Raises:
            ValueError: If the provided folder exists but is not a directory.

        Note:
            The actual storage folder becomes: folder/timestamp or folder/timestamp-N
            where N is a version number if the timestamp folder already exists.

            Folder is created with mode 0o700 (read/write/execute for owner only).

        Example:
            >>> from logger_36 as L
            >>> L.SetFolder("/var/log/myapp")
            # Creates /var/log/myapp/2025-10-17_103015/ or similar
        """
        if isinstance(folder, str):
            folder = path_t(folder)

        if isinstance(folder, path_t):
            if folder.exists() and not folder.is_dir():
                raise ValueError(f"{folder} exists and is not a folder.")

            if (folder / self.time_stamp).exists():
                version = 1
                while (folder / f"{self.time_stamp}-{version}").exists():
                    version += 1
                version = f"-{version}"
            else:
                version = ""
            folder /= f"{self.time_stamp}{version}"
            folder.mkdir(mode=0o700, parents=True)

        self.folder = folder

    def _AddHistoricalEvent(self, event: str, /) -> None:
        """"""
        now = date_time_t.now()
        if self.proxy is None:
            self.history[now] = event
        else:
            history = self.proxy.history
            history[now] = event
            self.proxy.history = history

    def handle(self, record: l.LogRecord, /) -> None:
        """
        Process a log record with enhanced functionality.

        This method extends the standard logging.Logger.handle() with:
        - Message holding/buffering when enabled
        - Automatic date separators when the date changes
        - Timestamp or elapsed time calculation
        - Source location tracking
        - Memory usage measurement (when enabled)
        - Process exit on ERROR/CRITICAL (when configured)

        Args:
            record (l.LogRecord): The log record to process. Will be modified in-place
                with additional attributes like WHERE_ATTR, WHEN_OR_ELAPSED_ATTR.

        Note:
            This method is typically called internally by the logging framework.
            Direct calls should be rare and carefully considered.

            In multiprocess mode, holding logic uses a multiprocessing.Value and Queue.
            In single-process mode, uses a boolean flag and regular list.

            Memory usage is recorded before the actual logging to capture the state
            at the point of the log call.

        Side Effects:
            - May exit the process (sys.exit(1)) if exit_on_error or exit_on_critical
              is True and the log level matches
            - Updates last_message_now and last_message_date
            - May append to memory_usages if monitoring is enabled
            - May insert date separator rules into the log output
        """
        if self.proxy is None:
            in_charge, using_proxy = self, False
        else:
            in_charge, using_proxy = self.proxy, True

        if in_charge.should_hold_messages:
            if using_proxy:
                in_charge.on_hold = in_charge.on_hold + [record]
            else:
                in_charge.on_hold.append(record)
            return

        now = date_time_t.now()
        if (date := now.date()) != in_charge.last_message_date:
            in_charge.last_message_date = date
            in_charge.DisplayRule(message=f"DATE: {date:{DATE_FORMAT}}")

        level = record.levelno

        # When.
        if getattr(record, SHOW_WHEN_ATTR, True):
            if now - in_charge.last_message_now > LONG_ENOUGH:
                w_or_e = f"{now:{TIME_FORMAT}}"
            else:
                w_or_e = FormattedElapsedTime(now)  # or: f"{[...]:.<{TIME_LENGTH}}".
            setattr(record, WHEN_OR_ELAPSED_ATTR, w_or_e)
        in_charge.last_message_now = now

        # Where.
        should_show_where = getattr(record, SHOW_WHERE_ATTR, level != l.INFO)
        if should_show_where or in_charge.should_monitor_memory_usage:
            where = f"{record.pathname}:{record.funcName}:{record.lineno}"
            if should_show_where:
                setattr(record, WHERE_ATTR, where)
            if in_charge.should_monitor_memory_usage:
                process_name = getattr(
                    record,
                    PROCESS_NAME_ATTR,
                    getattr(record, "processName", UNKNOWN_PROCESS_NAME),
                )
                in_charge._DoRecordMemoryUsage(using_proxy, where, process_name)

        # What.
        if not isinstance(record.msg, str):
            record.msg = str(record.msg)

        base_t.handle(in_charge, record)

        if (in_charge.exit_on_critical and (level is l.CRITICAL)) or (
            in_charge.exit_on_error and (level is l.ERROR)
        ):
            # Also works if in_charge.exit_on_error and record.levelno is l.CRITICAL
            # since __post_init__ set in_charge.exit_on_critical if
            # in_charge.exit_on_error.
            s.exit(1)

    def ToggleWarningInterceptions(self, state: bool, /) -> None:
        """
        Enable or disable interception of Python warnings.

        When enabled, Python warnings are captured and routed through this logger
        with enhanced formatting showing the warning type, message, and source location.

        Args:
            state (bool): True to enable interception, False to disable.

        Side Effects:
            - Modifies the handle method of Python's warning logger
            - Calls logging.captureWarnings() to enable/disable warning capture
            - Adds an entry to the logger's history

        Note:
            This method is idempotent - enabling when already enabled or disabling
            when already disabled has no effect.

            The original handle method is preserved in intercepted_wrn_handle and
            restored when interception is disabled.

        Example:
            >>> from logger_36 as L
            >>> L.ToggleWarningInterceptions(True)
            >>> import warnings
            >>> warnings.warn("This will be logged through logger")
        """
        if state:
            if self.intercepts_warnings:
                return

            logger = l.getLogger(WARNING_LOGGER_NAME)
            self.intercepted_wrn_handle = logger.handle
            logger.handle = t.MethodType(HandleForWarnings(self), logger)

            l.captureWarnings(True)
            self._AddHistoricalEvent("Warning Interception: ON")
        else:
            if not self.intercepts_warnings:
                return

            logger = l.getLogger(WARNING_LOGGER_NAME)
            logger.handle = self.intercepted_wrn_handle
            self.intercepted_wrn_handle = None

            l.captureWarnings(False)
            self._AddHistoricalEvent("Warning Interception: OFF")

    def ToggleLogInterceptions(self, state: bool, /) -> None:
        """
        Enable or disable interception of logs from other Python loggers.

        When enabled, all log messages from other loggers (except the warnings logger)
        are also routed through this logger with a suffix indicating the source logger.

        Args:
            state (bool): True to enable interception, False to disable.

        Side Effects:
            - Modifies the handle methods of all existing loggers
            - Stores original handle methods in intercepted_log_handles
            - Adds an entry to the logger's history with list of intercepted loggers
            - Clears _should_activate_log_interceptions flag

        Note:
            This method is idempotent - enabling when already enabled or disabling
            when already disabled has no effect.

            If _should_activate_log_interceptions is True (meaning activation was
            deferred until first handler was added), this method returns early to
            avoid premature activation.

            Only loggers that exist at the time of calling are intercepted. Loggers
            created afterward are not automatically intercepted.

        Example:
            >>> from logger_36 as L
            >>> L.ToggleLogInterceptions(True)
            >>> other_logger = l.getLogger("other")
            >>> other_logger.error(
            ...     "Error message"
            ... )  # Appears in logger with ":other:" suffix
        """
        if state:
            if self._should_activate_log_interceptions or self.intercepts_logs:
                return

            # Note: Alternative to self.manager is logging.root.manager.
            all_loggers_names_but_root = self.manager.loggerDict.keys()
            all_loggers = [l.getLogger()] + [
                l.getLogger(_)
                for _ in all_loggers_names_but_root
                if _ not in (self.name, WARNING_LOGGER_NAME)
            ]
            for logger in all_loggers:
                self.intercepted_log_handles[logger.name] = logger.handle
                logger.handle = t.MethodType(
                    HandleForInterceptions(logger, self), logger
                )

            intercepted = sorted(self.intercepted_log_handles.keys())
            if intercepted.__len__() > 0:
                as_str = ", ".join(intercepted)
                self._AddHistoricalEvent(f"Now Intercepting LOGs from: {as_str}")
        else:
            if self._should_activate_log_interceptions:
                self._should_activate_log_interceptions = False
                return

            if not self.intercepts_logs:
                return

            for name, handle in self.intercepted_log_handles.items():
                logger = l.getLogger(name)
                logger.handle = handle
            self.intercepted_log_handles.clear()
            self._AddHistoricalEvent("Log Interception: OFF")

    def ToggleExceptionInterceptions(self, state: bool, /) -> None:
        """
        Enable or disable interception of uncaught exceptions.

        When enabled, uncaught exceptions in both the main thread and other threads
        are caught, logged at CRITICAL level with full traceback, and the process
        is terminated with exit code 1.

        Args:
            state (bool): True to enable interception, False to disable and restore
                default exception handling.

        Side Effects:
            - Replaces sys.excepthook and threading.excepthook
            - Sets intercepts_exceptions flag
            - Adds an entry to the logger's history

        Note:
            This method is idempotent - enabling when already enabled or disabling
            when already disabled has no effect.

            When disabled, the original exception hooks (sys.__excepthook__ and
            threading.__excepthook__) are restored.

        Warning:
            When exception interception is enabled, ALL uncaught exceptions will
            terminate the process after logging. This is by design for production
            logging but may interfere with debugging.

        Example:
            >>> from logger_36 as L
            >>> L.ToggleExceptionInterceptions(True)
            >>> raise ValueError("This will be logged and then exit")
        """
        if state:
            if self.intercepts_exceptions:
                return

            s.excepthook = self.DealWithException
            thrd.excepthook = self.DealWithExceptionInThread
            self.intercepts_exceptions = True
            self._AddHistoricalEvent("Exception Interception: ON")
        else:
            if not self.intercepts_exceptions:
                return

            s.excepthook = s.__excepthook__
            thrd.excepthook = thrd.__excepthook__
            self.intercepts_exceptions = False
            self._AddHistoricalEvent("Exception Interception: OFF")

    def ActivateMemoryUsageMonitoring(self) -> None:
        """
        Enable memory usage monitoring for all subsequent log calls.

        When activated, each log call will measure and record current process memory
        usage and total system memory. The measurements are stored in memory_usages.

        Side Effects:
            - Sets should_monitor_memory_usage flag to True
            - Adds an entry to the logger's history
            - If memory measurement is not available, logs an error instead

        Note:
            Memory monitoring requires platform-specific modules to be available
            (checked via MEMORY_MEASURE_IS_AVAILABLE constant). If unavailable,
            should_monitor_memory_usage is set to False and an error is logged.

            Memory measurements add some overhead to each log call. Use judiciously
            in performance-critical code.

        Example:
            >>> from logger_36 as L
            >>> L.ActivateMemoryUsageMonitoring()
            >>> L.info("Test message")  # Memory usage is recorded
            >>> print(L.max_memory_usage)  # View peak memory
        """
        if MEMORY_MEASURE_IS_AVAILABLE:
            # Useless if called from __post_init__.
            self.should_monitor_memory_usage = True
            self._AddHistoricalEvent(
                f'Memory usage monitoring activated for logger "{self.name}"'
            )
        else:
            self.should_monitor_memory_usage = False
            self.error(MEMORY_MEASURE_ERROR)

    def AddHandler(
        self,
        handler_t_or_handler: type[base_handler_h]
        | base_handler_h
        | l.Handler
        | l.FileHandler,
        /,
        *,
        name: str | None = None,
        level: int = l.INFO,
        message_width: int = -1,
        **kwargs,
    ) -> None:
        """
        Add a logging handler to this logger with enhanced configuration.

        Accepts either a handler class (will be instantiated) or an already-instantiated
        handler. If a class with a "New" class method is provided, that method is used
        for instantiation with the provided parameters.

        Args:
            handler_t_or_handler (type[base_handler_h] | base_handler_h | l.Handler | l.FileHandler):
                Either a handler class to instantiate or an already-created handler instance.
            name (str | None, optional): Name for the handler. Defaults to None.
            level (int, optional): Logging level for this handler. Defaults to logging.INFO.
            message_width (int, optional): Width for message formatting. -1 means no limit.
                Defaults to -1.
            **kwargs: Additional keyword arguments passed to the handler's New() method
                or constructor.

        Side Effects:
            - Adds the handler to the logger's handlers list
            - Records handler addition in the logger's history
            - If _should_activate_log_interceptions is True, activates log interception
            - On instantiation errors, logs the error instead of raising

        Note:
            This method checks for a deferred log interception activation on the first
            handler addition. This ensures all loggers exist before interception starts.

            The method prefers using a "New" class method if available on handler classes,
            which allows for more sophisticated initialization patterns.

        Example:
            >>> from logger_36 as L
            >>> L.AddHandler(
            ...     l.FileHandler,
            ...     name="file_log",
            ...     level=l.DEBUG,
            ...     filename="/var/log/app.log",
            ... )
            >>> # Or with pre-instantiated handler:
            >>> L.AddHandler(l.FileHandler("/var/log/app.log"))
        """
        if self._should_activate_log_interceptions:
            # Turn _should_activate_log_interceptions off before calling
            # ToggleLogInterceptions because it checks it.
            self._should_activate_log_interceptions = False
            self.ToggleLogInterceptions(True)

        if isinstance(handler_t_or_handler, type):
            NewInstance = getattr(handler_t_or_handler, "New", None)
            if NewInstance is None:
                try:
                    handler = handler_t_or_handler()
                except Exception as exception:
                    self.error(
                        f"Error instantiating a handler of type "
                        f'"{type(handler_t_or_handler).__name__}":\n{exception}'
                    )
                    return
            else:
                handler = NewInstance(
                    name=name, message_width=message_width, level=level, **kwargs
                )
        else:
            handler = handler_t_or_handler
        base_t.addHandler(self, handler)

        path = getattr(handler, "baseFilename", "")
        if isinstance(path, path_t) or (path.__len__() > 0):
            path = f"\nPath: {path}"
        self._AddHistoricalEvent(
            f'New handler "{handler.name}" of type "{type(handler).__name__}" and '
            f"level {handler.level}={l.getLevelName(handler.level)}{path}"
        )

    def MakeMonochrome(self) -> None:
        """
        Add a monochrome console handler to the logger.

        Creates and adds a basic console handler without color formatting. Useful
        for environments that don't support ANSI color codes or when plain text
        output is preferred.

        Side Effects:
            - Adds a console_handler_t to the logger
            - Records the handler addition in the logger's history

        Example:
            >>> from logger_36 import L
            >>> L.MakeMonochrome()
            >>> L.info("This appears in plain text on console")
        """
        self.AddHandler(console_handler_t)

    def MakeRich(self, *, theme: str | theme_t | None = None) -> None:
        """
        Add a Rich-formatted console handler to the logger.

        Creates and adds a console handler with Rich library formatting, providing
        colored, beautifully formatted output with syntax highlighting and more.

        Args:
            theme (str | theme_t | None, optional): Theme configuration for Rich
                formatting. Can be a theme name string or theme object. Defaults to None
                (uses default theme).

        Side Effects:
            - Adds a console_rich_handler_t to the logger if Rich is available
            - If Rich is not available, logs an error message instead
            - Records the handler addition in the logger's history

        Note:
            If the Rich library is not installed, this method logs an error via
            MISSING_RICH_MESSAGE and does not add a handler.

        Example:
            >>> from logger_36 import L
            >>> L.MakeRich(theme="monokai")
            >>> L.info("This appears with Rich formatting")
        """
        if not RICH_IS_AVAILABLE:
            self.error(MISSING_RICH_MESSAGE)

        self.AddHandler(console_rich_handler_t, theme=theme)

    def MakePermanent(self, path: str | path_t, /) -> None:
        """
        Add a file handler to write logs to a permanent file.

        Creates and adds a file handler that writes log output to the specified
        file path. The file persists after the logger is destroyed.

        Args:
            path (str | path_t): File path where logs should be written. Can be
                either a string path or Path object.

        Side Effects:
            - Adds a file_handler_t to the logger
            - Creates the log file at the specified path
            - Records the handler addition in the logger's history

        Example:
            >>> from logger_36 import L
            >>> L.MakePermanent("/var/log/myapp/application.log")
            >>> L.info("This is written to the file")
        """
        self.AddHandler(file_handler_t, path=path)

    def ToggleShareability(self, state: bool, /) -> None:
        """
        Enable or disable multiprocess safe logging.

        Args:
            state (bool): True to enable multiprocess safety, False to disable.

        Raises:
            AssertionError: If not called from the main process or self is not a
            singleton instance.

        Note:
            The method is idempotent - enabling when already enabled or disabling when
            already disabled has no effect.

        Example:
            >>> from logger_36 import L
            >>> L.MakeRich()
            >>> L.ToggleShareability(True)  # Enable before spawning processes
            >>>
            >>> # Now safe to log from child processes
            >>> import multiprocessing as p
            >>> def worker():
            ...     L.info("Log from child process")
            >>>
            >>> process = p.Process(target=worker)
            >>> process.start()
            >>> process.join()
            >>>
            >>> L.ToggleShareability(False)  # Disable to flush remaining logs
        """
        assert self._is_singleton
        ToggleShareability(self, state)
        self._AddHistoricalEvent(f"Shareability: {state}")

    def __call__(self, *args, **kwargs) -> None:
        """
        Log arguments in a print-like style for quick debugging.

        Allows the logger to be called like a print function: logger(arg1, arg2, ...).
        The arguments are converted to strings, joined, and logged at INFO level
        with the calling location automatically included.

        Args:
            *args: Values to log, will be converted to strings and joined.
            **kwargs: Additional keyword arguments. The special 'separator' kwarg
                controls how args are joined (default: " "). Other kwargs are
                passed as extra data to the log record.

        Side Effects:
            - Logs a message at INFO level
            - Includes source location where the logger was called

        Example:
            >>> from logger_36 import L
            >>> L.MakeRich()
            >>> x, y = 10, 20
            >>> L(x, y, "sum is", x + y)
            # Logs: "10 20 sum is 30" with source location
            >>>
            >>> L("Values:", x, y, separator=" | ")
            # Logs: "Values: | 10 | 20"
        """
        separator = kwargs.pop("separator", " ")
        where = WhereInCode(with_relative_path=True)
        self.info(
            f"{separator.join(map(str, args))}\n{WHERE_SEPARATOR} {where}", extra=kwargs
        )

    def Log(
        self,
        message: str,
        /,
        *,
        level: int | str = l.ERROR,
        actual: h.Any = NOT_PASSED,
        expected: h.Any | None = None,
        expected_is_choices: bool = False,
        expected_op: expected_op_h = "=",
        with_final_dot: bool = True,
        **extra,
    ) -> None:
        """
        Log a message with optional actual/expected value comparison.

        Provides a convenient way to log messages that compare an actual value
        against an expected value or set of choices, with automatic formatting
        of the comparison.

        Args:
            message (str): The main log message.
            level (int | str, optional): Logging level as integer (e.g., logging.ERROR)
                or string (e.g., "ERROR"). Defaults to logging.ERROR.
            actual (Any, optional): The actual value encountered. If NOT_PASSED,
                no comparison is added. Defaults to NOT_PASSED.
            expected (Any | None, optional): The expected value or values.
                Defaults to None.
            expected_is_choices (bool, optional): If True, expected is treated as
                a collection of valid choices rather than a single expected value.
                Defaults to False.
            expected_op (expected_op_h, optional): Comparison operator to use when
                formatting ("=", "!=", "<", ">", etc.). Defaults to "=".
            with_final_dot (bool, optional): If True, ensures message ends with
                a period. Defaults to True.
            **extra: Additional key-value pairs to attach to the log record.

        Side Effects:
            - Logs the message at the specified level
            - Adds HAS_ACTUAL_EXPECTED_ATTR to the record's extra data if
              actual/expected comparison was formatted

        Example:
            >>> from logger_36 import L
            >>> L.Log("Configuration invalid", level="ERROR", actual=5, expected=10)
            # Logs: "Configuration invalid. Actual: 5, Expected: 10"
            >>>
            >>> L.Log(
            ...     "Invalid choice",
            ...     actual="red",
            ...     expected=["blue", "green", "yellow"],
            ...     expected_is_choices=True,
            ... )
            # Logs: "Invalid choice. Actual: red, Expected one of: blue, green, yellow"
        """
        if isinstance(level, str):
            level = l.getLevelNamesMapping()[level.upper()]
        message, has_actual_expected = MessageWithActualExpected(
            message,
            actual=actual,
            expected=expected,
            expected_is_choices=expected_is_choices,
            expected_op=expected_op,
            with_final_dot=with_final_dot,
        )
        extra[HAS_ACTUAL_EXPECTED_ATTR] = has_actual_expected
        self.log(level, message, extra=extra)

    def LogAsIs(self, message: str, /) -> None:
        """
        Log a message with minimal formatting at INFO level.

        Logs the message without timestamp, location information, or other
        automatic decorations. Useful for logging pre-formatted output or
        displaying raw text.

        Args:
            message (str): The message to log exactly as provided.

        Side Effects:
            - Logs at INFO level
            - Disables SHOW_WHEN_ATTR and SHOW_WHERE_ATTR for this record

        Note:
            Also available as info_raw() for consistency with standard logging methods.

        Example:
            >>> from logger_36 import L
            >>> L.MakeRich()
            >>> L.LogAsIs("=" * 50)
            >>> L.LogAsIs("REPORT SECTION")
            >>> L.LogAsIs("=" * 50)
            # Logs raw text without timestamp or location
        """
        self.log(l.INFO, message, extra={SHOW_WHEN_ATTR: False, SHOW_WHERE_ATTR: False})

    info_raw = LogAsIs  # To follow the convention of the logging methods info, error...

    def LogException(
        self, exception: Exception, /, *, level: int | str = l.ERROR
    ) -> None:
        """
        Log an exception with full traceback formatting.

        Formats and logs the exception with its complete traceback, similar to
        how Python displays uncaught exceptions.

        Args:
            exception (Exception): The exception instance to log.
            level (int | str, optional): Logging level as integer or string.
                Defaults to logging.ERROR.

        Side Effects:
            - Logs the formatted exception at the specified level
            - Disables SHOW_WHERE_ATTR since traceback provides location info

        Note:
            The output includes the exception type, message, and full traceback
            with a "----" separator for clarity.

        Example:
            >>> from logger_36 import L
            >>> try:
            ...     result = 10 / 0
            ... except ZeroDivisionError as e:
            ...     L.LogException(e, level="WARNING")
            # Logs:
            # Exception of type ZeroDivisionError
            # ----
            # Traceback (most recent call last):
            #   File "...", line X, in <module>
            #     result = 10 / 0
            # ZeroDivisionError: division by zero
        """
        if isinstance(level, str):
            level = l.getLevelNamesMapping()[level.upper()]
        # Extract of tcbk.format_exception documentation: The return value is a list of
        # strings, each ending in a newline [...]
        lines = tcbk.format_exception(exception)
        formatted = "".join(lines)[:-1]  # Discard the final "\n".
        message = f"Exception of type {type(exception).__name__}\n----\n{formatted}"
        self.log(level, message, extra={SHOW_WHERE_ATTR: False})

    def DealWithException(self, _, exc_value, exc_traceback, /) -> None:
        """
        Handle uncaught exceptions when exception interception is enabled.

        This is the callback function installed as sys.excepthook when
        ToggleExceptionInterceptions(True) is called. It logs the exception
        at CRITICAL level and exits the process.

        Args:
            _ (type): Exception type (unused, required by excepthook signature).
            exc_value (Exception): The exception instance.
            exc_traceback (traceback): The traceback object.

        Side Effects:
            - Logs the exception at CRITICAL level with full traceback
            - Calls sys.exit(1) to terminate the process

        Note:
            This method should not be called directly. It's automatically invoked
            by Python when an uncaught exception occurs and interception is enabled.
        """
        exception = exc_value.with_traceback(exc_traceback)
        self.LogException(exception, level=l.CRITICAL)
        s.exit(1)

    def DealWithExceptionInThread(self, args, /) -> None:
        """
        Handle uncaught exceptions in threads when exception interception is enabled.

        This is the callback function installed as threading.excepthook when
        ToggleExceptionInterceptions(True) is called. It delegates to
        DealWithException for consistent exception handling.

        Args:
            args (threading.ExceptHookArgs): NamedTuple containing:
                - exc_type: Exception type
                - exc_value: Exception instance
                - exc_traceback: Traceback object
                - thread: Thread where exception occurred

        Side Effects:
            - Logs the exception at CRITICAL level with full traceback
            - Calls sys.exit(1) to terminate the process

        Note:
            This method should not be called directly. It's automatically invoked
            by Python when an uncaught exception occurs in a thread and interception
            is enabled.
        """
        self.DealWithException(args.exc_type, args.exc_value, args.exc_traceback)

    def value(
        self,
        name: str,
        /,
        *,
        layout: value_layout_h | h.Any = "str",
        purpose: str | None = None,
        suffix: str = "",
        StorableValue: h.Callable[[h.Any], str | bytes] | None = None,
        StorableStr: h.Callable[[str], str | bytes] | None = None,
        epilogue: str = "\n",
        mode: str = "w",
        **values,
    ):
        """
        Log one or more values to a file in the logger's storage folder.

        Creates a file containing the provided values in the specified format.
        Useful for saving data snapshots, intermediate results, or debugging
        information to disk.

        Args:
            name (str): Base name for the output file (without extension).
            layout (value_layout_h | Any, optional): Output format:
                - "str": Convert values to strings (default)
                - "raw": Pickle serialize values (binary)
                - Custom: Actual value is ignored. Equivalent to "str", but suffix is
                not forced to be "txt".
                Defaults to "str".
            purpose (str | None, optional): Subfolder name for organizing outputs.
                If provided, file is created in folder/purpose/. Defaults to None.
            suffix (str, optional): File extension. Auto-determined for some layouts
                (e.g., "pkl" for raw, "txt" for str). Defaults to "".
            StorableValue (Callable[[Any], str | bytes] | None, optional): Custom
                function to convert values to storable format. If provided, layout
                is ignored. Defaults to None.
            StorableStr (Callable[[str], str | bytes] | None, optional): Custom
                function to convert strings to storable format. Defaults to None.
            epilogue (str, optional): String to append at end of file. Defaults to "\n".
            mode (str, optional): File open mode ("w" for text, "wb" for binary).
                Defaults to "w".
            **values: Key-value pairs to store. Keys become labels in multi-value
                output.

        Side Effects:
            - Creates a file in the logger's storage folder
            - If file exists, appends a unique suffix to avoid overwriting

        Raises:
            Logs an error if no values are provided.

        Example:
            >>> logger = logger_t(folder="/tmp/logs")
            >>> logger.MakeRich()
            >>>
            >>> # Single value
            >>> logger.value("result", result=42)
            # Creates: /tmp/logs/TIMESTAMP/result.txt with content "42\n"
            >>>
            >>> # Multiple values
            >>> logger.value("metrics", accuracy=0.95, loss=0.23, epoch=10)
            # Creates file with content:
            # accuracy = 0.95
            # loss = 0.23
            # epoch = 10
            >>>
            >>> # Binary pickle format
            >>> data = {"key": [1, 2, 3]}
            >>> logger.value("data", layout="raw", data=data)
            # Creates: /tmp/logs/TIMESTAMP/data.pkl (binary)
            >>>
            >>> # Organized by purpose
            >>> logger.value("checkpoint", purpose="training", weights=[...])
            # Creates: /tmp/logs/TIMESTAMP/training/checkpoint.txt
        """
        if values.__len__() == 0:
            self.error("No values passed for logging")
            return

        if StorableValue is None:
            if layout == "raw":
                suffix = "pkl"
                StorableValue = PickleStringOf
                StorableStr = str.encode
                epilogue = ""
                mode = "wb"
            elif layout == "str":
                if suffix in (None, ""):
                    suffix = "txt"
                StorableValue = str
                StorableStr = lambda _: _
            else:
                StorableValue = str
                if StorableStr is None:
                    StorableStr = lambda _: _
        elif StorableStr is None:
            StorableStr = lambda _: _

        epilogue = StorableStr(epilogue)
        is_equal_to = StorableStr(" = ")

        if values.__len__() > 1:
            content = []
            for key, value in values.items():
                content.append(StorableStr(key) + is_equal_to + StorableValue(value))
            content = StorableStr("\n").join(content)
        else:
            content = StorableValue(values[tuple(values.keys())[0]])

        path = self.StoragePath(name, purpose=purpose, suffix=suffix)
        if path.exists():
            path = NewUniqueName(path)

        with open(path, mode) as accessor:
            accessor.write(content + epilogue)

    def file(self, path: path_t | str, /, *, purpose: str | None = None):
        """
        Copy a file to the logger's storage folder.

        Duplicates an existing file into the logger's organized storage structure,
        preserving the original file's metadata (timestamps, permissions).

        Args:
            path (path_t | str): Path to the source file to copy.
            purpose (str | None, optional): Subfolder name for organizing the copy.
                If provided, file is copied to folder/purpose/. Defaults to None.

        Side Effects:
            - Copies the file to the logger's storage folder
            - If destination exists, creates a unique name to avoid overwriting
            - Preserves file metadata using shutil.copy2

        Example:
            >>> logger = logger_t(folder="/var/log/myapp")
            >>> logger.MakeRich()
            >>>
            >>> # Copy a config file for reference
            >>> logger.file("/etc/myapp/config.ini")
            # Creates: /var/log/myapp/TIMESTAMP/config.ini
            >>>
            >>> # Organize by purpose
            >>> logger.file("model.pkl", purpose="checkpoints")
            # Creates: /var/log/myapp/TIMESTAMP/checkpoints/model.pkl
        """
        output = self.StoragePath(path.stem, purpose=purpose, suffix=path.suffix)
        if output.exists():
            output = NewUniqueName(output)

        shll.copy2(path, output)

    def DisplayRule(
        self, /, *, message: str | None = None, color: str | None = None
    ) -> None:
        """
        Display a horizontal rule separator in the log output.

        Creates a visual separator line, optionally with a centered message.
        Useful for organizing log output into sections.

        Args:
            message (str | None, optional): Text to display centered in the rule.
                If None, displays a plain rule line. Defaults to None.
            color (str | None, optional): Color name for the rule (handler-dependent).
                Only effective with color-supporting handlers. Defaults to None.

        Side Effects:
            - Logs a special record at INFO level with SHOW_W_RULE_ATTR set
            - If color is specified, adds RULE_COLOR_ATTR to the record

        Note:
            The actual appearance depends on the handler. Rich handlers will
            display an attractive horizontal rule, while plain handlers might
            show dashes or similar.

        Example:
            >>> from logger_36 import L
            >>> L.MakeRich()
            >>>
            >>> L.DisplayRule(message="INITIALIZATION")
            >>> L.info("Starting application")
            >>> L.DisplayRule()  # Plain separator
            >>> L.info("Processing data")
            >>> L.DisplayRule(message="COMPLETE", color="green")
        """
        record = {
            "name": self.name,
            "levelno": l.INFO,  # For management by logging.Logger.handle.
            "msg": message,
            SHOW_W_RULE_ATTR: True,
        }
        if color is not None:
            record[RULE_COLOR_ATTR] = color
        record = l.makeLogRecord(record)
        base_t.handle(self, record)

    def ToggleLogHolding(self, state: bool, /) -> None:
        """
        Enable or disable buffering of log messages.

        When enabled, log records are queued rather than immediately processed.
        This is useful for delaying log output until a certain point, or for
        grouping related logs together.

        Args:
            state (bool): True to start holding messages, False to release and
                process all held messages.

        Side Effects:
            - When enabling: Sets should_hold_messages flag/value to True
            - When disabling:
                - Sets should_hold_messages flag/value to False
                - Processes all held messages in order
                - Clears the on_hold queue/list

        Note:
            This method is safe to call regardless of current holding state.
            In multiprocess mode, uses a multiprocessing.Value for the flag
            and a Queue for held records. In single-process mode, uses a boolean
            flag and a list.

            Held messages are processed in FIFO order when released.

        Example:
            >>> from logger_36 import L
            >>> L.MakeRich()
            >>>
            >>> L.ToggleLogHolding(True)
            >>> L.info("Message 1")  # Held
            >>> L.info("Message 2")  # Held
            >>> L.info("Message 3")  # Held
            >>> L.ToggleLogHolding(False)  # All three now appear in order
            >>>
            >>> def PerformOperation():
            ...     return 0
            >>>
            >>> # Useful for conditional logging
            >>> L.ToggleLogHolding(True)
            >>> result = PerformOperation()
            >>> if result is None:
            ...     L.ToggleLogHolding(False)  # Show the logs
            ... else:
            ...     L.on_hold.clear()  # Discard the logs
        """
        if state:
            self.should_hold_messages = True
        else:
            self.should_hold_messages = False
            for record in self.on_hold:
                self.handle(record)
            self.on_hold.clear()

    def AddContextLevel(self, new_level: str, /) -> None:
        """
        Add a context level to the context stack.

        Context levels are used to organize staged issues hierarchically. Each
        level represents a nested operation or scope.

        Args:
            new_level (str): The context label to add to the stack.

        Side Effects:
            - Appends new_level to the context_levels list

        Note:
            Context levels are removed via the context manager protocol (__exit__)
            or manually via PopIssues. They're primarily used with the issue
            staging system.

        Example:
            >>> from logger_36 import L
            >>> L.AddContextLevel("DataValidation")
            >>> L.StageIssue("Missing field")
            >>> L.AddContextLevel("UserInput")
            >>> L.StageIssue("Invalid email")
            >>> L.CommitIssues()
            # Logs issues with context: DataValidation > UserInput > Invalid email
        """
        if self.proxy is None:
            self.context_levels.append(new_level)
        else:
            proxy = self.proxy
            proxy.context_levels = proxy.context_levels + [new_level]

    def AddedContextLevel(self, new_level: str, /) -> h.Self:
        """
        Add a context level and return self for use as a context manager.

        This method enables the "with" statement syntax for managing context levels,
        automatically removing the level when exiting the with block.

        Args:
            new_level (str): The context label to add to the stack.

        Returns:
            logger_t: Returns self to enable context manager protocol.

        Side Effects:
            - Appends new_level to the context_levels list
            - The level is automatically removed when exiting the with block

        Example:
            >>> from logger_36 import L
            >>> L.MakeRich()
            >>>
            >>> with L.AddedContextLevel("DatabaseOperations"):
            ...     L.StageIssue("Connection timeout")
            ...     with L.AddedContextLevel("QueryExecution"):
            ...         L.StageIssue("Syntax error in SQL")
            ...     L.CommitIssues()
            # Issues are logged with hierarchical context labels
            # "DatabaseOperations" level is automatically removed after the block
        """
        self.AddContextLevel(new_level)
        return self

    def StageIssue(
        self,
        message: str,
        /,
        *,
        level: int = l.ERROR,
        actual: h.Any = NOT_PASSED,
        expected: h.Any | None = None,
        expected_is_choices: bool = False,
        expected_op: expected_op_h = "=",
        with_final_dot: bool = False,
    ) -> None:
        """
        Stage an issue for later batch logging instead of logging immediately.

        Issues are accumulated with their context levels and can be logged all at
        once using CommitIssues(). This is useful for validation routines that
        collect multiple errors before reporting them.

        Args:
            message (str): The issue description.
            level (int, optional): Logging level for this issue. Defaults to logging.ERROR.
            actual (Any, optional): The actual value encountered. If NOT_PASSED,
                no comparison is added. Defaults to NOT_PASSED.
            expected (Any | None, optional): The expected value or values.
                Defaults to None.
            expected_is_choices (bool, optional): If True, expected is treated as
                a collection of valid choices. Defaults to False.
            expected_op (expected_op_h, optional): Comparison operator for formatting.
                Defaults to "=".
            with_final_dot (bool, optional): If True, ensures message ends with
                a period. Defaults to False.

        Side Effects:
            - Appends a tuple (issue_t, has_actual_expected) to staged_issues
            - The issue includes current context levels for hierarchical organization

        Note:
            Staged issues are NOT logged until CommitIssues() is called. This allows
            collecting multiple issues and then deciding whether to log them, or
            discarding them if the operation ultimately succeeds.

        Example:
            >>> from logger_36 import L
            >>> L.MakeRich()
            >>>
            >>> def validate_user(data):
            ...     with L.AddedContextLevel("UserValidation"):
            ...         if not data.get("email"):
            ...             L.StageIssue("Email is required")
            ...         if not data.get("age"):
            ...             L.StageIssue("Age is required")
            ...         elif data["age"] < 18:
            ...             L.StageIssue(
            ...                 "User too young",
            ...                 actual=data["age"],
            ...                 expected=18,
            ...                 expected_op=">=",
            ...             )
            ...
            ...         if L.has_staged_issues:
            ...             L.CommitIssues()  # Log all issues at once
            ...             return False
            ...         return True
        """
        context = ISSUE_CONTEXT_SEPARATOR.join(self.context_levels)
        issue = NewIssue(
            context,
            ISSUE_CONTEXT_END,
            message,
            level=level,
            actual=actual,
            expected=expected,
            expected_is_choices=expected_is_choices,
            expected_op=expected_op,
            with_final_dot=with_final_dot,
        )
        if self.proxy is None:
            self.staged_issues.append(issue)
        else:
            proxy = self.proxy
            proxy.staged_issues = proxy.staged_issues + [issue]

    def PopIssues(
        self, /, *, should_remove_context: bool = False
    ) -> list[tuple[str, bool]]:
        """
        Retrieve and remove all staged issues without logging them.

        Extracts staged issues, optionally strips their context information, and
        clears the staged_issues list. Useful for custom issue processing or
        transferring issues to another system.

        Args:
            should_remove_context (bool, optional): If True, removes all context
                information from issues. If False, keeps context but removes the
                level prefix. Defaults to False.

        Returns:
            list[tuple[str, bool]]: List of tuples containing:
                - issue message (str): The formatted issue text
                - has_actual_expected (bool): Whether issue includes actual/expected

        Side Effects:
            - Clears the staged_issues list
            - Returns empty list if no issues were staged

        Example:
            >>> from logger_36 import L
            >>> L.AddContextLevel("Validation")
            >>> L.StageIssue("Invalid input")
            >>> L.StageIssue("Missing field")
            >>>
            >>> issues = L.PopIssues()
            >>> for issue_text, has_comparison in issues:
            ...     print(f"Issue: {issue_text}")
            # Issue: Validation > Invalid input
            # Issue: Validation > Missing field
            >>>
            >>> L.has_staged_issues  # False, issues were popped
        """
        if not self.has_staged_issues:
            return []

        output = []

        if should_remove_context:
            separator = ISSUE_CONTEXT_END
        else:
            separator = ISSUE_LEVEL_SEPARATOR
        separator_length = separator.__len__()
        for issue, has_actual_expected in self.staged_issues:
            start_idx = issue.find(separator)
            issue = issue[(start_idx + separator_length) :]
            output.append((issue, has_actual_expected))

        if self.proxy is None:
            self.staged_issues.clear()
        else:
            self.proxy.staged_issues = []

        return output

    def CommitIssues(
        self, /, *, order: order_h = "when", unified: bool = False
    ) -> None:
        """
        Log all staged issues and clear the staging area.

        Processes all accumulated issues, logging them either individually or as
        a unified message. Issues can be ordered by staging time or by context.

        Args:
            order (order_h, optional): How to order issues before logging:
                - "when": Log in the order they were staged (default)
                - "context": Sort alphabetically by context string
                Defaults to "when".
            unified (bool, optional): If True, combines all issues into a single
                log entry at the level of the first issue. If False, logs each
                issue separately at its own level. Defaults to False.

        Side Effects:
            - Logs all staged issues at their respective levels
            - Clears the staged_issues list
            - Does nothing if no issues are staged
            - Disables SHOW_WHERE_ATTR since issues track their own locations

        Warning:
            If any issue has a level that triggers process exit (ERROR with
            exit_on_error=True or CRITICAL with exit_on_critical=True), subsequent
            issues will not be logged as the process will terminate.

        Note:
            Issues are logged with stacklevel=2 to show the caller's location
            rather than the CommitIssues location.

        Example:
            >>> from logger_36 import L
            >>> L.MakeRich()
            >>>
            >>> with L.AddedContextLevel("Configuration"):
            ...     L.StageIssue("Port not specified", level=l.WARNING)
            ...     L.StageIssue("Invalid timeout value", level=l.ERROR)
            >>>
            >>> with L.AddedContextLevel("Database"):
            ...     L.StageIssue("Connection failed", level=l.CRITICAL)
            >>>
            >>> # Log individually in staged order
            >>> L.CommitIssues(order="when", unified=False)
            # Logs three separate messages
            >>>
            >>> # Or combine into one message at first issue's level
            >>> L.CommitIssues(order="context", unified=True)
            # Logs one combined message, sorted by context
        """
        assert order in h.get_args(order_h)

        if not self.has_staged_issues:
            return

        if order == "when":
            issues = self.staged_issues
        else:  # order == "context"
            issues = sorted(
                self.staged_issues,
                key=lambda _: _[0].split(ISSUE_LEVEL_SEPARATOR, maxsplit=1)[1],
            )
        """
        Format issues as an exception:
        try:
            raise ValueError("\n" + "\n".join(issues))
        except ValueError as exception:
            lines = ["Traceback (most recent call last):"] + tcbk.format_stack()[:-1]
            lines[-1] = lines[-1][:-1]
            lines.extend(tcbk.format_exception_only(exception))
            formatted = "\n".join(lines)
        """

        extra = {SHOW_WHERE_ATTR: False}
        if unified:
            level, _ = issues[0][0].split(ISSUE_LEVEL_SEPARATOR, maxsplit=1)
            wo_level = []
            any_has_actual_expected = False
            for issue, has_actual_expected in issues:
                _, issue = issue.split(ISSUE_LEVEL_SEPARATOR, maxsplit=1)
                if has_actual_expected:
                    any_has_actual_expected = True
                wo_level.append(issue)
            if any_has_actual_expected:
                extra[HAS_ACTUAL_EXPECTED_ATTR] = True
            self.log(int(level), "\n".join(wo_level), stacklevel=2, extra=extra)
        else:
            for issue, has_actual_expected in issues:
                level, issue = issue.split(ISSUE_LEVEL_SEPARATOR, maxsplit=1)
                if has_actual_expected:
                    extra[HAS_ACTUAL_EXPECTED_ATTR] = True
                self.log(int(level), issue, stacklevel=2, extra=extra)
                if has_actual_expected:
                    del extra[HAS_ACTUAL_EXPECTED_ATTR]
        if self.proxy is None:
            self.staged_issues.clear()
        else:
            self.proxy.staged_issues = []

    def SetCheckpoint(self, name: str, /, *, process_name: str | None = None) -> None:
        """
        Record a named timestamp checkpoint.

        Captures the current time with a descriptive name and process identifier.
        Useful for performance analysis and timing different stages of execution.

        Args:
            name (str): Descriptive label for this checkpoint.
            process_name (str | None, optional): When self is shared and the process
                start method is forkserver or spawn, this method is always called from
                the main process. This argument is meant to be set by the subprocess to
                work around this.

        Side Effects:
            - Appends tuple (name, process_name, timestamp) to intermediate_times

        Example:
            >>> from logger_36 import L
            >>> L.MakeRich()
            >>>
            >>> def ProcessData():
            ...     pass
            >>>
            >>> L.SetCheckpoint("StartProcessing")
            >>> ProcessData()
            >>> L.SetCheckpoint("EndProcessing")
            >>>
            >>> # Later, analyze timing
            >>> times = L.intermediate_times
            >>> start = next(t for name, _, t in times if name == "StartProcessing")
            >>> end = next(t for name, _, t in times if name == "EndProcessing")
            >>> duration = end - start
            >>> print(f"Processing took {duration.total_seconds()} seconds")
        """
        if process_name is None:
            process_name = prll.current_process().name
        intermediate_time = (name, process_name, date_time_t.now())
        if self.proxy is None:
            self.intermediate_times.append(intermediate_time)
        else:
            proxy = self.proxy
            proxy.intermediate_times = proxy.intermediate_times + [intermediate_time]

    def RecordMemoryUsage(self, /, *, process_name: str | None = None) -> None:
        """
        Manually record current memory usage at this point in code.

        Captures memory usage measurement independently of automatic monitoring.
        Requires memory measurement capabilities to be available on the platform.

        Args:
            process_name (str | None, optional): When self is shared and the process
                start method is forkserver or spawn, this method is always called from
                the main process. This argument is meant to be set by the subprocess to
                work around this.

        Side Effects:
            - Appends tuple (location, process_name, current_usage, total_usage)
              to memory_usages
            - Does nothing if memory measurement is not available

        Note:
            Unlike automatic memory monitoring (which records on every log call),
            this allows selective measurement at specific points of interest.

            The location is captured from the calling code, not from RecordMemoryUsage.

        Example:
            >>> from logger_36 import L
            >>> L.MakeRich()
            >>>
            >>> def LoadedDataset():
            ...     return {}
            >>>
            >>> L.RecordMemoryUsage()
            >>> large_data = LoadedDataset()
            >>> L.RecordMemoryUsage()
            >>>
            >>> # Check memory increase
            >>> before = L.memory_usages[-2][-1]
            >>> after = L.memory_usages[-1][-1]
            >>> print(f"Memory increased by {after - before} bytes")
        """
        if MEMORY_MEASURE_IS_AVAILABLE:
            if self.proxy is None:
                in_charge, using_proxy = self, False
            else:
                in_charge, using_proxy = self.proxy, True
            if process_name is None:
                process_name = prll.current_process().name
            in_charge._DoRecordMemoryUsage(using_proxy, WhereInCode(), process_name)

    def _DoRecordMemoryUsage(
        self, self_is_proxy: bool, where: str, process_name: str, /
    ) -> None:
        """See RecordMemoryUsage."""
        usage, total = CurrentMemoryUsage(root_pid=self.pid)
        memory_usage = (where, process_name, usage, total)
        if self_is_proxy:
            self.memory_usages = self.memory_usages + [memory_usage]
        else:
            self.memory_usages.append(memory_usage)

    def StoragePath(
        self, name: str, /, *, purpose: str | None = None, suffix: str = ""
    ) -> path_t:
        """
        Generate a file path in the logger's storage folder structure.

        Creates an appropriate path for storing logger-related files, automatically
        handling folder creation and avoiding name conflicts.

        Args:
            name (str): Base filename without extension.
            purpose (str | None, optional): Subfolder for organizing files.
                If provided, creates folder/purpose/name. Defaults to None.
            suffix (str, optional): File extension. Auto-prepends "." if missing.
                Defaults to "".

        Returns:
            Path: Complete file path. If the file already exists, returns a path
                with a unique suffix to avoid overwriting.

        Side Effects:
            - Creates parent directories with mode 0o700 if they don't exist
            - If no logger folder is configured, attempts to use handler base paths
            - Falls back to temporary file if no storage location is available

        Note:
            Can be used as a static method by passing a logger as self:
            `logger_t.StoragePath(logger, "filename", suffix="txt")`

        Example:
            >>> logger = logger_t(folder="/var/log/myapp")
            >>> logger.MakeRich()
            >>>
            >>> # Simple file in root
            >>> path = logger.StoragePath("results", suffix="json")
            # Returns: /var/log/myapp/TIMESTAMP/results.json
            >>>
            >>> # Organized by purpose
            >>> path = logger.StoragePath("model", purpose="checkpoints", suffix="pkl")
            # Returns: /var/log/myapp/TIMESTAMP/checkpoints/model.pkl
            >>>
            >>> # If results.json already exists, returns unique name
            >>> path2 = logger.StoragePath("results", suffix="json")
            # Returns: /var/log/myapp/TIMESTAMP/results-1.json
        """
        if (suffix.__len__() > 0) and (suffix[0] != "."):
            suffix = f".{suffix}"

        if self.folder is None:
            for handler in self.handlers:
                if (path := getattr(handler, "baseFilename", None)) is None:
                    continue

                output = (path_t(path).parent / name).with_suffix(suffix)
                if output.exists():
                    continue

                return output

            return NewTemporaryFile(suffix)

        if purpose is None:
            output = self.folder / name
        else:
            output = self.folder / purpose / name
        output = output.with_suffix(suffix)
        if output.exists():
            output = NewUniqueName(output)

        output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)

        return output

    def __enter__(self) -> None:
        """
        Enter the context manager (no-op).

        Allows the logger to be used with the "with" statement when combined
        with AddedContextLevel or similar patterns.

        Returns:
            None

        Note:
            This is a placeholder implementation. The real functionality is in
            __exit__ which removes context levels.
        """
        pass

    def __exit__(
        self,
        exc_type: Exception | None,
        exc_value: str | None,
        traceback: traceback_t | None,
        /,
    ) -> bool:
        """
        Exit the context manager by removing the top context level.

        Automatically called when exiting a "with" block. Removes the most
        recently added context level from the context stack.

        Args:
            exc_type (Exception | None): Exception type if an exception occurred.
            exc_value (str | None): Exception message if an exception occurred.
            traceback (traceback_t | None): Traceback if an exception occurred.

        Returns:
            bool: Always returns False, allowing exceptions to propagate.

        Side Effects:
            - Removes the top element from context_levels list

        Note:
            This enables automatic context cleanup when using AddedContextLevel
            with the "with" statement.

        Example:
            >>> from logger_36 import L
            >>> with L.AddedContextLevel("Operation"):
            ...     L.StageIssue("Error occurred")
            ...     # Context level is automatically removed here
            >>> len(L.context_levels)  # 0
        """
        _ = self.context_levels.pop()
        return False
