"""Human-friendly formatter with level colors and appended extras.

Use ``PrettyFormatter`` when logs are primarily read by people on a TTY:
- it colors messages by level when enabled, and leaves output untouched otherwise
- it appends any non-standard `extra` fields as ``key=value`` pairs so contextual data stays visible

Example dictConfig entry:

```
{
    "formatters": {
        "pretty": {
            "format": "%(asctime)s %(levelname)s %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "()": "logging_blueprint.formatter.pretty.PrettyFormatter",
        }
    }
}
```

This is aimed at human-friendly displays; use a structured formatter instead when machine parsing is required.
"""

from __future__ import annotations

import logging
import logging.config

from logging_blueprint.formatter.utils import colorize, extract_extras, use_colors


class PrettyFormatter(logging.Formatter):
    """Colorizes human-readable logs and preserves contextual extras."""

    def __init__(self, fmt: str, datefmt: str, color: bool | None = None) -> None:
        """Initialize an instance of `PrettyFormatter`."""
        super().__init__(fmt=fmt, datefmt=datefmt)
        self._color_enabled = use_colors(color)

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record.

        This function delegates to the superclass, then appends extras. It also applies colorization.
        """
        s = super().format(record)
        extras = extract_extras(record)
        if extras:
            s = f"{s} " + " ".join(f"{k}={v}" for k, v in extras.items())
        return colorize(record.levelno, s, self._color_enabled)
