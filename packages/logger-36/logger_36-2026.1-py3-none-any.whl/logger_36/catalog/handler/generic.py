"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import logging as l
import typing as h

from logger_36.catalog.config.optional import RICH_IS_AVAILABLE

if RICH_IS_AVAILABLE:
    from logger_36.catalog.handler.console_rich import MakeThemeRich
    from rich.console import Console as console_t
    from rich.rule import Rule as rule_t
    from rich.terminal_theme import DEFAULT_TERMINAL_THEME
    from rich.text import Text as text_t
else:
    console_t = rule_t = DEFAULT_TERMINAL_THEME = text_t = None

from logger_36.type.handler import non_file_handler_t as base_t
from logger_36.type.theme import theme_t


class generic_handler_t(base_t):
    def __init__(
        self,
        name: str | None,
        message_width: int,
        level: int,
        theme: theme_t,
        supports_html: bool,
        EmitMessage: h.Callable[[str], None],
        kwargs,
    ) -> None:
        """"""
        base_t.__init__(self, name, message_width, level, theme, kwargs)

        self.EmitMessage = EmitMessage
        self.is_rich = False
        self.console = None  # console_t | None.
        self.console_options = None  # rich.console.ConsoleOptions | None.

        self.__post_init_local__(supports_html)

    def __post_init_local__(self, supports_html: bool, /) -> None:
        """"""
        if supports_html and (console_t is not None):
            self.is_rich = True
            self.console = console_t(highlight=False, force_terminal=True)
            self.console_options = self.console.options.update(
                overflow="ignore", no_wrap=True
            )
            MakeThemeRich(self.theme)

    @classmethod
    def New(
        cls,
        /,
        *,
        name: str | None = None,
        message_width: int = -1,
        level: int = l.NOTSET,
        theme: theme_t | None = None,
        supports_html: bool = False,
        EmitMessage: h.Callable[[str], None] | None = None,
        **kwargs,
    ) -> h.Self:
        """
        EmitMessage: By definition, the generic handler does not know how to output
        messages. If not passed, it defaults to output-ing messages in the console.
        """
        assert EmitMessage is not None

        if supports_html and (console_t is not None) and (theme is None):
            theme = theme_t.NewDefault("rich", "dark")

        return cls(
            name, message_width, level, theme, supports_html, EmitMessage, kwargs
        )

    def Rule(
        self, /, *, text: str | None = None, color: str | None = None
    ) -> str | rule_t:
        """"""
        if (color is None) and (self.theme is not None):
            color = self.theme.rule

        if self.is_rich:
            if text is None:
                return rule_t(style=color)
            return rule_t(title=text_t(text, style=f"bold {color}"), style=color)

        return base_t.Rule(self, text=text, color=color)

    def emit(self, record: l.LogRecord, /) -> None:
        """"""
        if self.is_rich:
            message = self.MessageFromRecord(record)
            segments = self.console.render(message, options=self.console_options)

            # Inspired from the code of: rich.console.export_html.
            html_segments = []
            for text, style, _ in segments:
                if text == "\n":
                    html_segments.append("\n")
                else:
                    if style is not None:
                        style = style.get_html_style(DEFAULT_TERMINAL_THEME)
                        if (style is not None) and (style.__len__() > 0):
                            text = f'<span style="{style};">{text}</span>'
                    html_segments.append(text)
            if html_segments[-1] == "\n":
                html_segments = html_segments[:-1]

            # /!\ For some reason, the widget splits the message into lines, place each
            # line inside a pre tag, and set margin-bottom of the first and list lines
            # to 12px. This can be seen by printing self.contents.toHtml(). To avoid the
            # unwanted extra margins, margin-bottom is set to 0 below.
            message = (
                "<pre style='margin-bottom:0px'>" + "".join(html_segments) + "</pre>"
            )
        else:
            message = self.MessageFromRecord(record)

        self.EmitMessage(message)
