"""
Theme class theme_t.

SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import types as t
import typing as h

from logger_36.constant.theme import COLORS_TERMINAL_256, LAYOUT_ON_BACKGROUND
from logger_36.hint.theme import (
    color_h,
    colorized_message_fct_h,
    for_background_h,
    layout_h,
)


class theme_t:
    """
    A class to represent a theme configuration with specific colors and settings for
    different parts of the message.

    Attributes:
        level (dict[int, color_h]): A dictionary mapping log levels to their respective
            colors.
        text (color_h): The color for plain text in the theme.
        actual (color_h): The color used to display 'actual' values in messages.
        expected (color_h): The color used to display 'expected' values in messages.
        where (color_h): The color used to highlight locations or contexts in messages.
        rule (color_h): The color used for displaying rules or boundaries within a
            message.
        background_alt (color_h | None): An alternate background color, if enabled. Can
            be `None`.
        should_alternate_background (bool): A flag to determine if the background should
            alternate between messages. For messages in general (theme configuration).
        should_set_background (bool): A flag to enable or disable setting a background
            color for specific messages. For the current message (only for runtime
            usage).
        ColorizedMessage (colorized_message_fct_h | None): Function to apply
            colorization to messages, if provided.

    Notes:
        Colors in the default themes can be specified as:
            - names of the terminal-256 set (see COLORS_TERMINAL_256 in
            logger_36.constant.theme),
            - hexadecimal RGB strings, starting with the "#" character as usual,
            - 3-tuples of 8-bit integers.
    """

    def __init__(self) -> None:
        """
        Initialize a new theme configuration with invalid default colors.

        The only purpose of the initialization is to inform the IDE of the attributes.
        """
        self.level: dict[int, color_h] = {}
        self.text: color_h = ""
        self.actual: color_h = ""
        self.expected: color_h = ""
        self.where: color_h = ""
        self.rule: color_h = ""
        self.background_alt: color_h | h.Any | None = None
        #
        self.should_alternate_background: bool = False
        self.should_set_background: bool = False

        self.ColorizedMessage: colorized_message_fct_h | None = None

    @classmethod
    def NewDefault(
        cls,
        layout: layout_h,
        for_background: for_background_h,
        /,
        *,
        should_alternate_background: bool = False,
        ColorizedMessage: colorized_message_fct_h | None = None,
    ) -> h.Self:
        """
        Create a new default theme configuration based on the specified layout and
        background type.

        Args:
            layout (layout_h): The layout type for the theme. Must be one of the
                possible values defined by `layout_h`.
            for_background (for_background_h): The background type to use, either 'dark'
                or 'light'.
            should_alternate_background (bool, optional): Whether to alternate the
                background color between messages. Defaults to `False`.
            ColorizedMessage (colorized_message_fct_h | None, optional): Function for
                colorizing messages. Defaults to `None`.

        Returns:
            h.Self: An instance of the theme configuration with default colors set
                according to the layout and background type.

        Raises:
            AssertionError: If the provided layout or background type is not recognized.
        """
        assert (layout in h.get_args(layout_h)) and (
            for_background in h.get_args(for_background_h)
        )

        output = cls()

        if for_background == "dark":
            from logger_36.catalog.config.theme_on_dark import (
                ACTUAL_COLOR,
                ALTERNATIVE_BACKGROUND,
                EXPECTED_COLOR,
                LEVEL_COLOR,
                RULE_COLOR,
                TEXT_COLOR,
                WHERE_COLOR,
            )
        else:
            from logger_36.catalog.config.theme_on_light import (
                ACTUAL_COLOR,
                ALTERNATIVE_BACKGROUND,
                EXPECTED_COLOR,
                LEVEL_COLOR,
                RULE_COLOR,
                TEXT_COLOR,
                WHERE_COLOR,
            )
        if layout == "html":
            AppropriateVersionOf = _HexVersionOf
        else:
            AppropriateVersionOf = _Terminal256VersionOf
        (
            ACTUAL_COLOR,
            ALTERNATIVE_BACKGROUND,
            EXPECTED_COLOR,
            RULE_COLOR,
            TEXT_COLOR,
            WHERE_COLOR,
        ) = AppropriateVersionOf(
            ACTUAL_COLOR,
            ALTERNATIVE_BACKGROUND,
            EXPECTED_COLOR,
            RULE_COLOR,
            TEXT_COLOR,
            WHERE_COLOR,
        )
        LEVEL_COLOR = {_: AppropriateVersionOf(__) for _, __ in LEVEL_COLOR.items()}

        output.level = LEVEL_COLOR
        output.text = TEXT_COLOR
        output.actual = ACTUAL_COLOR
        output.expected = EXPECTED_COLOR
        output.where = WHERE_COLOR
        output.rule = RULE_COLOR
        output.background_alt = ALTERNATIVE_BACKGROUND

        output.should_alternate_background = should_alternate_background
        if ColorizedMessage is not None:
            output.SetColorizedMessageFunction(ColorizedMessage)

        return output

    @classmethod
    def NewDefaultFromStr(cls, theme: str, /) -> h.Self:
        """
        Create a new default theme configuration from a string representation of layout
        and background type.

        Args:
            theme (str): A string containing the layout type and background type
                separated by `LAYOUT_ON_BACKGROUND`.

        Returns:
            h.Self: An instance of the theme configuration with default colors set
                according to the parsed layout and background type.

        Raises:
            AssertionError: If the string format is incorrect or the components cannot
                be parsed.
        """
        parameters = theme.split(LAYOUT_ON_BACKGROUND)
        assert parameters.__len__() == 2
        return cls.NewDefault(*parameters)

    def SetColorizedMessageFunction(
        self, ColorizedMessage: colorized_message_fct_h, /
    ) -> None:
        """
        Set the function to be used for colorizing messages.

        Args:
            ColorizedMessage (colorized_message_fct_h): The function that will perform
                message colorization.
        """
        self.ColorizedMessage = t.MethodType(ColorizedMessage, self)


def _HexVersionOf(*colors) -> str | list[str]:
    """
    Convert colors to their hexadecimal representation if they are not already in that
    format.

    Args:
        *colors: Variable number of color inputs which can be strings or tuples/lists
            representing RGB values.

    Returns:
        Union[str, List[str]]: A string or list of strings containing the hexadecimal
            color representation.
    """
    output = []

    for color in colors:
        if isinstance(color, str) and (color[0] != "#"):
            color = color.replace("_", "").lower()
            color = f"#{COLORS_TERMINAL_256[color][1]}"
        elif isinstance(color, tuple):
            color = "#" + "".join(hex(_)[2:] for _ in color)
        output.append(color)

    if output.__len__() > 1:
        return output
    return output[0]


def _Terminal256VersionOf(*colors) -> str | list[str]:
    """
    Convert colors to their terminal-256 bit representation if they are not already in
    that format.

    Args:
        *colors: Variable number of color inputs which can be strings or tuples/lists
            representing RGB values.

    Returns:
        Union[str, List[str]]: A string or list of strings containing the terminal-256
            color representation.
    """
    output = []

    largest_distance = 3 * 255**2
    for color in colors:
        if isinstance(color, str) and (color[0] == "#"):
            color = tuple(int(color[_ : (_ + 2)]) for _ in (1, 3, 5))
        if isinstance(color, tuple):
            closest, distance_closest = None, largest_distance
            for name, (_, _, current) in COLORS_TERMINAL_256.items():
                distance = sum(
                    (_ - __) ** 2 for _, __ in zip(color, current, strict=True)
                )
                if distance < distance_closest:
                    closest, distance_closest = name, distance
            color = closest
        output.append(color)

    if output.__len__() > 1:
        return output
    return output[0]
