"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from logger_36.constant.message import LINE_BREAK


def WrappedLines(lines: list[str], message_width: int, /) -> list[str]:
    """"""
    output = []

    for line in lines:
        while line.__len__() > message_width:
            if " " in line[(message_width - 1) : (message_width + 1)]:
                piece, line = (
                    line[: (message_width - 1)].rstrip(),
                    line[(message_width - 1) :].lstrip(),
                )
            elif line[message_width - 2] == " ":
                piece, line = (
                    line[: (message_width - 2)].rstrip(),
                    line[(message_width - 1) :],
                )
            else:
                piece, line = (line[: (message_width - 1)], line[(message_width - 1) :])
            output.append(piece + LINE_BREAK)

        output.append(line)

    return output
