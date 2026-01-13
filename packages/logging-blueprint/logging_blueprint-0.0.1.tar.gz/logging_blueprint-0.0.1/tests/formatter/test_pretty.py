"""Unit tests for logging_blueprint/formatter/pretty.py."""

from __future__ import annotations

import logging
import os
from unittest import mock

from logging_blueprint.formatter.pretty import PrettyFormatter


def test_format_appends_extras_without_color_when_not_tty() -> None:
    class NonSerializable:
        def __repr__(self) -> str:
            return "NonSerializable"

    record = logging.LogRecord("demo", logging.INFO, __file__, 123, "hello %s", ("world",), None)
    record.request_id = "abc123"
    record.user_id = 42
    record.context = NonSerializable()

    with (
        mock.patch("sys.stderr.isatty", return_value=False),
        mock.patch("sys.stdout.isatty", return_value=False),
    ):
        formatter = _make_formatter()

    formatted = formatter.format(record)

    assert formatted == "INFO:hello world request_id=abc123 user_id=42 context=NonSerializable"


def test_format_colors_output_when_tty_available() -> None:
    with mock.patch("sys.stderr.isatty", return_value=True), mock.patch("sys.stdout.isatty", return_value=True):
        formatter = _make_formatter()

    formatted = formatter.format(logging.LogRecord("demo", logging.ERROR, __file__, 123, "boom", (), None))

    assert formatted == "\x1b[31mERROR:boom\x1b[0m"


def test_color_codes_match_levels_with_tty() -> None:
    expectations = {
        logging.ERROR: "31",
        logging.WARNING: "33",
        logging.INFO: "32",
        logging.DEBUG: "36",
    }

    with (
        mock.patch("sys.stderr.isatty", return_value=True),
        mock.patch("sys.stdout.isatty", return_value=True),
    ):
        formatter = _make_formatter()

    for level, code in expectations.items():
        record = logging.LogRecord("demo", level, __file__, 1, "msg", (), None)
        formatted = formatter.format(record)
        assert formatted == f"\x1b[{code}m{logging.getLevelName(level)}:msg\x1b[0m"


def test_no_color_env_disables_output() -> None:
    with (
        mock.patch.dict(os.environ, {"NO_COLOR": "1"}, clear=False),
        mock.patch("sys.stderr.isatty", return_value=True),
        mock.patch("sys.stdout.isatty", return_value=True),
    ):
        formatter = _make_formatter()

    formatted = formatter.format(logging.LogRecord("demo", logging.ERROR, __file__, 123, "boom", (), None))
    assert formatted == "ERROR:boom"


def _make_formatter() -> PrettyFormatter:
    return PrettyFormatter("%(levelname)s:%(message)s", "%H:%M:%S")
