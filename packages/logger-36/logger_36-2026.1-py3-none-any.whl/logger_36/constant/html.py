"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

LOCAL_HOST = "localhost"
HTML_SUFFIX = ".htm"


TITLE_PLACEHOLDER = "TITLE"
BODY_PLACEHOLDER = "BODY"

MINIMAL_HTML = f"""
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{TITLE_PLACEHOLDER}</title>
    </head>
    <body>
        <pre>
{BODY_PLACEHOLDER}
        </pre>
    </body>
</html>
"""


LOGGING_PAGE = b"""
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
    </head>
    <body>
        <pre id="messages"></pre>
        <script>
            const source = new EventSource("/stream");
            source.onmessage = function(event) {
                const messages = document.getElementById("messages");
                messages.innerHTML += event.data + "<br>";
            };
        </script>
    </body>
</html>
"""
