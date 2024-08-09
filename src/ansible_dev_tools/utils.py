"""Utility function not requiring server dependencies."""

from __future__ import annotations


class Colors:
    """ANSI color codes.

    Attributes:
        BLACK: Black color.
        RED: Red color.
        GREEN: Green color.
        BROWN: Brown color.
        BLUE: Blue color.
        PURPLE: Purple color.
        CYAN: Cyan color.
        LIGHT_GRAY: Light gray color.
        DARK_GRAY: Dark gray color.
        LIGHT_RED: Light red color.
        LIGHT_GREEN: Light green color.
        YELLOW: Yellow color.
        LIGHT_BLUE: Light blue color.
        LIGHT_PURPLE: Light purple color.
        LIGHT_CYAN: Light cyan color.
        LIGHT_WHITE: Light white color.
        BOLD: Bold text.
        FAINT: Faint text.
        ITALIC: Italic text.
        UNDERLINE: Underline text.
        BLINK: Blink text.
        NEGATIVE: Negative text.
        CROSSED: Crossed text.
        END: Reset color.
    """

    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"
