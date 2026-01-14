"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import logging as l
import typing as h

from logger_36.config.message import ACTUAL_PATTERNS, EXPECTED_PATTERN
from logger_36.constant.message import CONTEXT_LENGTH_p_1
from logger_36.type.handler import non_file_handler_t as base_t
from logger_36.type.theme import COLORS_TERMINAL_256, theme_t
from rich.color import Color as color_t  # noqa
from rich.console import Console as console_t  # noqa
from rich.markup import escape as EscapedVersion  # noqa
from rich.rule import Rule as rule_t  # noqa
from rich.style import Style as style_t  # noqa
from rich.text import Text as text_t  # noqa
from rich.traceback import install as InstallTracebackHandler  # noqa

_COMMON_TRACEBACK_ARGUMENTS = ("theme", "width")
_EXCLUSIVE_TRACEBACK_ARGUMENTS = (
    "extra_lines",
    "indent_guides",
    "locals_hide_dunder",
    "locals_hide_sunder",
    "locals_max_length",
    "locals_max_string",
    "max_framesshow_locals",
    "suppress",
    "word_wrap",
)


class console_rich_handler_t(base_t):
    def __init__(
        self,
        name: str | None,
        message_width: int,
        level: int,
        theme: theme_t,
        should_install_traceback: bool,
        kwargs,
    ) -> None:
        """"""
        base_t.__init__(self, name, message_width, level, theme, kwargs)
        self.console = None  # console_t | None.
        self.__post_init_local__(should_install_traceback, **kwargs)

    def __post_init_local__(self, should_install_traceback: bool, **kwargs) -> None:
        """"""
        traceback_kwargs = {}
        if should_install_traceback:
            for key in kwargs:
                if key in _COMMON_TRACEBACK_ARGUMENTS:
                    traceback_kwargs[key] = kwargs[key]
                elif key in _EXCLUSIVE_TRACEBACK_ARGUMENTS:
                    traceback_kwargs[key] = kwargs.pop(key)

        self.console = console_t(highlight=False, force_terminal=True, **kwargs)
        MakeThemeRich(self.theme)

        if should_install_traceback:
            traceback_kwargs["console"] = self.console
            InstallTracebackHandler(**traceback_kwargs)

    @classmethod
    def New(
        cls,
        /,
        *,
        name: str | None = None,
        message_width: int = -1,
        level: int = l.NOTSET,
        theme: theme_t | None = None,
        should_install_traceback: bool = False,
        **kwargs,
    ) -> h.Self:
        """"""
        if theme is None:
            theme = theme_t.NewDefault("rich", "dark")
        return cls(name, message_width, level, theme, should_install_traceback, kwargs)

    def Rule(
        self, /, *, text: str | None = None, color: str | None = None
    ) -> str | rule_t:
        """"""
        if color is None:
            color = self.theme.rule
        if text is None:
            return rule_t(style=color)
        return rule_t(title=text_t(text, style=f"bold {color}"), style=color)

    def emit(self, record: l.LogRecord, /) -> None:
        """"""
        message = self.MessageFromRecord(record)
        self.console.print(message, crop=False, overflow="ignore")


def MakeThemeRich(theme: theme_t, /) -> None:
    """"""
    theme.SetColorizedMessageFunction(_ColorizedMessage)
    if theme.should_alternate_background:
        # Done here to avoid adding the Rich dependency to the theme_t implementation.
        color = color_t.from_rgb(*COLORS_TERMINAL_256[theme.background_alt][2])
        theme.background_alt = style_t(bgcolor=color)


def _ColorizedMessage(
    theme: theme_t,
    log_level: int,
    when_or_elapsed_and_level: str,
    message: str,
    where_and_process: str,
    has_actual_expected: bool,
    /,
) -> text_t:
    """"""
    output = text_t(
        f"{when_or_elapsed_and_level}{message}{where_and_process}", theme.text
    )

    output.stylize(theme.level[log_level], end=CONTEXT_LENGTH_p_1)
    if has_actual_expected:
        _ = output.highlight_words(ACTUAL_PATTERNS, style=theme.actual)
        _ = output.highlight_regex(EXPECTED_PATTERN, style=theme.expected)
    if where_and_process.__len__() > 0:
        output.stylize(theme.where, start=CONTEXT_LENGTH_p_1 + message.__len__())

    if theme.should_alternate_background:
        if theme.should_set_background:
            output.stylize(theme.background_alt)
            theme.should_set_background = False
        else:
            theme.should_set_background = True

    return output
