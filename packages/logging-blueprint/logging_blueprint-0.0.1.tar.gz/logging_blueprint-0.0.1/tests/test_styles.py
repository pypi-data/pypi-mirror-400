"""Tests for style parsing/resolution helpers."""

from __future__ import annotations

from logging_blueprint.styles import LogStyle, parse_style


def test_parse_style_accepts_logfmt() -> None:
    assert parse_style("logfmt") is LogStyle.LOGFMT


def test_parse_style_accepts_color_alias() -> None:
    assert parse_style("color") is LogStyle.PRETTY
