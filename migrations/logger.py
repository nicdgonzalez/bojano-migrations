# Additional information about customizing the terminal via ANSI escape codes:
# https://en.wikipedia.org/wiki/ANSI_escape_code

import enum
import logging
import os
import sys

from overrides import override

FORCE_COLOR = os.getenv("FORCE_COLOR", False)


class Style(enum.IntEnum):
    RESET = 0
    BOLD = 1
    UNDERLINE = 4
    BLINK = 5
    REVERSE = 7
    CONCEAL = 8


class TextColor(enum.IntEnum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37  # This white is more like a really light gray.
    DEFAULT = 39
    BRIGHT_BLACK = 90
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN = 96
    BRIGHT_WHITE = 97  # This is more of a true white (i.e., RBG(255,255,255)).


def fix_logging_level_names() -> None:
    logging.addLevelName(logging.WARNING, "WARN")
    logging.addLevelName(logging.CRITICAL, "FATAL")


def terminal_suppors_color(stream=sys.stdout) -> bool:
    """Check whether the current terminal supports ANSI color codes."""
    if bool(FORCE_COLOR):
        return True

    return hasattr(stream, "isatty") and stream.isatty()


# Modified from Rapptz/discord.py:
# https://github.com/Rapptz/discord.py/blob/af75985730528fa76f9949ea768ae90fd2a50c75/discord/utils.py#L1294
class ColorFormatter(logging.Formatter):
    LEVEL_COLORS: list[tuple[int, str]] = [
        (logging.DEBUG, f"\x1b[{TextColor.CYAN};{Style.BOLD}m"),
        (logging.INFO, f"\x1b[{TextColor.GREEN};{Style.BOLD}m"),
        (logging.WARNING, f"\x1b[{TextColor.YELLOW};{Style.BOLD}m"),
        (logging.ERROR, f"\x1b[{TextColor.RED};{Style.BOLD}m"),
        (logging.CRITICAL, f"\x1b[{TextColor.MAGENTA};{Style.BOLD}m"),
    ]

    FORMATS: dict[int, str] = {
        level: logging.Formatter(
            fmt=f"\x1b[{TextColor.BRIGHT_BLACK}m%(asctime)s\x1b[{Style.RESET}m {color}%(levelname)-5s\x1b[{Style.RESET}m \x1b[{TextColor.BLUE}m%(name)s\x1b[{Style.RESET}m] %(message)s",  # noqa: E501
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
        for level, color in LEVEL_COLORS
    }

    @override
    def format(self, record: logging.LogRecord) -> str:
        formatter = self.FORMATS.get(record.levelno)

        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[{TextColor.RED}m{text}\x1b[{Style.RESET}m"

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


def enable_logging() -> None:
    fix_logging_level_names()

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 format
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(
        ColorFormatter() if terminal_suppors_color(sys.stdout) else formatter
    )

    logging.root.addHandler(stream_handler)
    logging.root.setLevel(logging.INFO)
