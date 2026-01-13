"""Unit tests for logging_blueprint/formatter/logfmt.py."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from unittest import mock

from logging_blueprint.formatter.logfmt import LOGFMT_DEFAULT_FMT, LogfmtFormatter


def test_format_includes_extras_without_color_when_not_tty() -> None:
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
        formatter = LogfmtFormatter(LOGFMT_DEFAULT_FMT, "%H:%M:%S")

    with mock.patch.object(formatter, "formatTime", return_value="2024-01-02 03:04:05"):
        formatted = formatter.format(record)

    expected = (
        'ts="2024-01-02 03:04:05" level=info logger=demo msg="hello world" '
        "request_id=abc123 user_id=42 context=NonSerializable"
    )
    assert formatted == expected


def test_format_colors_output_when_tty_available() -> None:
    record = logging.LogRecord("demo", logging.ERROR, __file__, 123, "boom", (), None)

    with mock.patch("sys.stderr.isatty", return_value=True), mock.patch("sys.stdout.isatty", return_value=True):
        formatter = LogfmtFormatter(LOGFMT_DEFAULT_FMT, "%H:%M:%S")

    with mock.patch.object(formatter, "formatTime", return_value="2024-01-02 03:04:05"):
        formatted = formatter.format(record)

    assert (
        formatted == 'ts=\x1b[90m"2024-01-02 03:04:05"\x1b[0m '
        "level=\x1b[31merror\x1b[0m "
        "logger=\x1b[90mdemo\x1b[0m "
        "msg=boom"
    )


def test_format_handles_collections_and_dataclasses() -> None:
    @dataclass
    class Payload:
        id: int
        label: str

        def __repr__(self) -> str:
            return f"Payload(id={self.id}, label='{self.label}')"

    record = logging.LogRecord("demo", logging.INFO, __file__, 123, "processing batch", (), None)
    record.payload = Payload(7, "alpha")
    record.attributes = {"count": 2, "nested": {"done": True}}
    record.items = ("first", 2, None)
    record.tags = ["a", "b"]
    record.success = True
    record.optional = None
    record.cost = 1.23

    with (
        mock.patch("sys.stderr.isatty", return_value=False),
        mock.patch("sys.stdout.isatty", return_value=False),
    ):
        formatter = LogfmtFormatter(LOGFMT_DEFAULT_FMT, "%H:%M:%S")

    with mock.patch.object(formatter, "formatTime", return_value="2024-01-02T03:04:05"):
        formatted = formatter.format(record)

    expected = (
        'ts=2024-01-02T03:04:05 level=info logger=demo msg="processing batch" '
        "payload=\"Payload(id=7, label='alpha')\" "
        "attributes=\"{'count': 2, 'nested': {'done': True}}\" "
        "items=\"('first', 2, None)\" tags=\"['a', 'b']\" success=true optional=null cost=1.23"
    )
    assert formatted == expected


def test_format_quotes_and_escapes_special_characters() -> None:
    message = 'multi word with "quotes" and backslash \\ value=42'
    record = logging.LogRecord("demo", logging.WARNING, __file__, 20, message, (), None)
    record.path = r"C:\tmp folder\file.txt"
    record.note = 'contains "double quotes" and \\backslashes\\'
    record.empty = ""

    with (
        mock.patch("sys.stderr.isatty", return_value=False),
        mock.patch("sys.stdout.isatty", return_value=False),
    ):
        formatter = LogfmtFormatter(LOGFMT_DEFAULT_FMT, "%H:%M:%S")

    with mock.patch.object(formatter, "formatTime", return_value="2024-02-03T04:05:06"):
        formatted = formatter.format(record)

    expected = (
        "ts=2024-02-03T04:05:06 level=warning logger=demo "
        'msg="multi word with \\"quotes\\" and backslash \\\\ value=42" '
        'path="C:\\\\tmp folder\\\\file.txt" note="contains \\"double quotes\\" and \\\\backslashes\\\\" empty=""'
    )
    assert formatted == expected
