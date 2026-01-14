"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import html
import http.server as http_t
import logging as l
import typing as h
import webbrowser as webb
from threading import Thread as thread_t

from logger_36.config.message import ACTUAL_PATTERN_COMPILED, EXPECTED_PATTERN_COMPILED
from logger_36.constant.html import LOCAL_HOST, LOGGING_PAGE
from logger_36.type.handler import non_file_handler_t as base_t
from logger_36.type.theme import theme_t


class http_handler_t(base_t):
    """
    Server-Sent Events (SSE) client
    """

    def __init__(
        self, name: str | None, message_width: int, level: int, theme: theme_t
    ) -> None:
        """"""
        base_t.__init__(self, name, message_width, level, theme)

        self.server = _server_t((LOCAL_HOST, 0), _handler_t)
        self.thread = thread_t(target=self.server.serve_forever, daemon=True)
        self.connexion = None

        self.__post_init_local__()

    def __post_init_local__(self) -> None:
        """"""
        _ = webb.open_new_tab(f"http://{LOCAL_HOST}:{self.server.server_port}")

        self.theme.SetColorizedMessageFunction(_ColorizedMessage)

        self.thread.start()
        while self.server.connexion is None:
            pass
        self.connexion = self.server.connexion

    @classmethod
    def New(
        cls,
        /,
        *,
        name: str | None = None,
        message_width: int = -1,
        level: int = l.NOTSET,
        theme: theme_t | None = None,
        **_,
    ) -> h.Self:
        """"""
        if theme is None:
            theme = theme_t.NewDefault("html", "light")
        return cls(name, message_width, level, theme)

    def Rule(self, /, *, text: str | None = None, color: str | None = None) -> str:
        """"""
        theme = self.theme
        if color is None:
            color = theme.rule

        output = f'<span style="color:{color};">{base_t.Rule(self, text=text)}</span>'
        if text is not None:
            output = output.replace(
                text, f'<span style="font-weight:bold;">{text}</span>'
            )

        return output

    def emit(self, record: l.LogRecord, /) -> None:
        """"""
        message = self.MessageFromRecord(record).replace("\n", "<br/>")

        connexion = self.connexion
        connexion.write(f"data: {message}\n\n".encode("utf-8"))
        connexion.flush()


def _ColorizedMessage(
    theme: theme_t,
    log_level: int,
    when_or_elapsed_and_level: str,
    message: str,
    where_and_process: str,
    has_actual_expected: bool,
    /,
) -> str:
    """"""
    when_or_elapsed_and_level = (
        f'<span style="color:{theme.level[log_level]};">'
        f"{when_or_elapsed_and_level}</span>"
    )

    message = html.escape(message)
    if has_actual_expected:
        for pattern, color in zip(
            (ACTUAL_PATTERN_COMPILED, EXPECTED_PATTERN_COMPILED),
            (theme.actual, theme.expected),
            strict=True,
        ):
            matches = tuple(pattern.finditer(message))
            if matches.__len__() == 0:
                continue

            pieces = []
            end_previous_p_1 = 0
            for match in matches:
                piece = match.group()
                start = match.start()

                pieces.extend(
                    (
                        message[end_previous_p_1:start],
                        f'<span style="color:{color};">{piece}</span>',
                    )
                )
                end_previous_p_1 = match.end()

            pieces.append(message[end_previous_p_1:])
            message = "".join(pieces)

    message = f'<span style="color:{theme.text};">{message}</span>'
    where_and_process = f'<span style="color:{theme.where};">{where_and_process}</span>'

    output = f"{when_or_elapsed_and_level}{message}{where_and_process}"

    if theme.should_alternate_background:
        if theme.should_set_background:
            output = (
                f'<span style="background-color:{theme.background_alt};">'
                f"{output}</span>"
            )
            theme.should_set_background = False
        else:
            theme.should_set_background = True

    return output


base_server_t = http_t.HTTPServer
base_handler_t = http_t.BaseHTTPRequestHandler


class _server_t(base_server_t):
    def __init__(self, *args, **kwargs) -> None:
        """"""
        base_server_t.__init__(self, *args, **kwargs)
        self.connexion = None

    def SetConnexion(self, connexion, /) -> None:
        """"""
        self.connexion = connexion


class _handler_t(base_handler_t):
    def do_GET(self) -> None:
        """"""
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(LOGGING_PAGE.__len__()))
            self.end_headers()

            self.wfile.write(LOGGING_PAGE)
        elif self.path == "/stream":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            self.server.SetConnexion(self.wfile)  # Must be here, not in "/" path.
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args, **kwargs) -> None:
        pass
