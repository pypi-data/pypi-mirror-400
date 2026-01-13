"""Logfmt-style formatter with optional colorization and extras."""

from __future__ import annotations

import logging
from typing import Any, Final

from logging_blueprint.formatter.utils import colorize_token, dim_token, extract_extras, use_colors

LOGFMT_DEFAULT_FMT: Final = "ts=%(asctime)s level=%(levelname)s logger=%(name)s msg=%(message)s"


class LogfmtFormatter(logging.Formatter):
    """Emit logfmt-style lines while preserving extras."""

    def __init__(self, fmt: str, datefmt: str, color: bool | None = None) -> None:
        """Initialize the formatter."""
        super().__init__(fmt=fmt, datefmt=datefmt)
        self._color_enabled = use_colors(color)

    def format(self, record: logging.LogRecord) -> str:
        """Render a log record as a logfmt string."""
        timestamp = self.formatTime(record, self.datefmt)
        base_parts = [
            f"ts={dim_token(_format_value(timestamp), self._color_enabled)}",
            f"level={colorize_token(record.levelno, _format_value(record.levelname.lower()), self._color_enabled)}",
            f"logger={dim_token(_format_value(record.name), self._color_enabled)}",
            f"msg={_format_value(record.getMessage())}",
        ]

        extras = extract_extras(record)
        if record.exc_info:
            extras["exc"] = self.formatException(record.exc_info)
        if record.stack_info:
            extras["stack"] = self.formatStack(record.stack_info)

        parts = base_parts + [f"{key}={_format_value(value)}" for key, value in extras.items()]
        return " ".join(parts)


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return _quote(str(value))


def _quote(text: str) -> str:
    if text == "":
        return '""'
    needs_quotes = any(ch.isspace() or ch in {"=", '"'} for ch in text)
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    if needs_quotes:
        return f'"{escaped}"'
    return escaped
