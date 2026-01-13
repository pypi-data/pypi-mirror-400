"""Utilities shared by various formatters."""

from __future__ import annotations

import json
import logging
import os
import sys
from collections.abc import Set
from typing import Any, Final

_STD_RECORD_KEYS: Final[Set[str]] = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "message",
    "asctime",
    "taskName",
    "task",
}


def extract_extras(record: logging.LogRecord) -> dict[str, Any]:
    """Given a LogRecord, extract any non-standard attributes.

    This function takes in a LogRecord and returns a dictionary of any attributes that are not part of the standard
    LogRecord keys. It also ensures that the values are JSON serializable, and if not, converts them to a string
    representation.

    Args:
        record: The log record from which to extract non-standard attributes.

    Returns:
        A mapping of non-standard attribute names to their values, with values converted to strings if they are not
        JSON serializable.
    """
    # LogRecord is dynamic; extras appear on __dict__.
    out: dict[str, Any] = {}
    for k, v in record.__dict__.items():
        if k in _STD_RECORD_KEYS:
            continue
        # Avoid unserializable objects in a basic way
        try:
            json.dumps(v)
            out[k] = v
        except Exception:
            out[k] = repr(v)
    return out


def require_python_json_logger() -> None:
    """Ensure that the 'python-json-logger' package is installed by importing it.

    This function can be used to check whether the 'python-json-logger' package is available in the current
    environment. The goal is to provide a simple, consistent error message to users if the package is not installed.
    There is some start-up overhead to this check, but it's a relatively small price to pay, especially since this
    should only ever be called once per process.

    Raises:
        RuntimeError: If the 'python-json-logger' package is not installed.
    """
    try:
        import importlib

        importlib.import_module("pythonjsonlogger.json")
    except ImportError as exc:  # pragma: no cover - exercised in integration paths
        msg = (
            "LogStyle.JSON requires optional dependency 'python-json-logger'. "
            "Install with `pip install logging-blueprint[json]` or add python-json-logger to your dependencies."
        )
        raise RuntimeError(msg) from exc


def use_colors(color: bool | None) -> bool:
    """Resolve whether color is enabled based on explicit config, env, and TTY."""
    if color is not None:
        return color
    if "NO_COLOR" in os.environ:
        return False
    return sys.stderr.isatty() or sys.stdout.isatty()


def colorize(levelno: int, s: str, color_enabled: bool) -> str:
    """Apply ANSI color codes to an entire string based on level when enabled."""
    code = _color_code(levelno) if color_enabled else None
    if code is None:
        return s
    return f"\x1b[{code}m{s}\x1b[0m"


def colorize_token(levelno: int, token: str, color_enabled: bool) -> str:
    """Apply ANSI color to a specific token, leaving surrounding text untouched."""
    code = _color_code(levelno) if color_enabled else None
    if code is None:
        return token
    return f"\x1b[{code}m{token}\x1b[0m"


def dim_token(token: str, color_enabled: bool) -> str:
    """Apply ANSI dim styling to a token when enabled."""
    if not color_enabled:
        return token
    return f"\x1b[90m{token}\x1b[0m"


def _color_code(levelno: int) -> str:
    if levelno >= logging.ERROR:
        return "31"  # red
    if levelno >= logging.WARNING:
        return "33"  # yellow
    if levelno >= logging.INFO:
        return "32"  # green
    return "36"  # cyan
