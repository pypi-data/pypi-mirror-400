"""Unit tests for logging_blueprint/conf.py.

NOTE: This package is **EXPERIMENTAL** and breaking changes should be expected, even to "public" interfaces.
Contributors are welcome to make _justifiable_ breaking changes to the package as-needed (along with accompanying
changes to this test suite).
"""

from __future__ import annotations

import io
import json
import logging
from unittest import mock

import pytest

from logging_blueprint.conf import (
    EnvLoggingConfig,
    build_dict_config_from_env,
    merge_env_into_dict_config,
)
from logging_blueprint.formatter.logfmt import LOGFMT_DEFAULT_FMT
from logging_blueprint.styles import LogStyle


def test_env_logging_blueprintig_from_env_parses_and_defaults() -> None:
    env_cfg = EnvLoggingConfig.from_env(
        {
            "PY_LOG": " ",
            "PY_LOG_STYLE": "pretty",
            "PY_LOG_STREAM": "stdout",
            "PY_LOG_FMT": "%(levelname)s:%(message)s",
            "PY_LOG_DATEFMT": "%H:%M:%S",
            "PY_LOG_DISABLE_EXISTING": "1",
        }
    )

    assert env_cfg.directives == ""
    assert env_cfg.style == LogStyle.PRETTY
    assert env_cfg.stream == "stdout"
    assert env_cfg.fmt == "%(levelname)s:%(message)s"
    assert env_cfg.datefmt == "%H:%M:%S"
    assert env_cfg.disable_existing_loggers is True


def test_merge_env_into_dict_config_installs_defaults_without_mutation() -> None:
    base = {
        "handlers": {"existing": {"class": "logging.NullHandler"}},
        "root": {"handlers": ["existing"]},
        "loggers": {"preserve": {"level": "ERROR"}},
    }
    env_cfg = EnvLoggingConfig(
        directives="debug,myapp.db=warn",
        style=LogStyle.PLAIN,
        stream="stdout",
        fmt="%(message)s",
        datefmt="%H:%M:%S",
        disable_existing_loggers=True,
    )

    merged = merge_env_into_dict_config(base, env_cfg)

    assert base == {
        "handlers": {"existing": {"class": "logging.NullHandler"}},
        "root": {"handlers": ["existing"]},
        "loggers": {"preserve": {"level": "ERROR"}},
    }
    assert merged is not base
    assert merged["disable_existing_loggers"] is True
    assert merged["formatters"]["envlog"]["format"] == "%(message)s"
    assert merged["handlers"]["envlog_console"]["stream"] == "ext://sys.stdout"
    assert "envlog_console" in merged["root"]["handlers"]
    assert merged["root"]["level"] == "DEBUG"
    assert merged["loggers"]["myapp.db"]["level"] == "WARNING"
    assert merged["loggers"]["preserve"]["level"] == "ERROR"


def test_build_dict_config_from_env_respects_base_without_mutation() -> None:
    base = {"handlers": {"existing": {"class": "logging.NullHandler"}}}
    env_cfg = EnvLoggingConfig(directives="warning")

    with mock.patch("sys.stderr.isatty", return_value=True), mock.patch("sys.stdout.isatty", return_value=True):
        built = build_dict_config_from_env(env_cfg, base=base)

    assert base == {"handlers": {"existing": {"class": "logging.NullHandler"}}}
    assert built["handlers"]["existing"]["class"] == "logging.NullHandler"
    assert built["root"]["level"] == "WARNING"
    assert built["version"] == 1


@pytest.mark.json_extra
def test_json_formatter_is_exposed_in_dict_config() -> None:
    cfg = build_dict_config_from_env(EnvLoggingConfig(directives="info", style=LogStyle.JSON))

    formatter_cfg = cfg["formatters"]["envlog"]
    assert formatter_cfg["()"] == "pythonjsonlogger.json.JsonFormatter"


def test_logfmt_formatter_is_exposed_in_dict_config() -> None:
    cfg = build_dict_config_from_env(EnvLoggingConfig(directives="info", style=LogStyle.LOGFMT))

    formatter_cfg = cfg["formatters"]["envlog"]
    assert formatter_cfg["()"] == "logging_blueprint.formatter.logfmt.LogfmtFormatter"
    assert formatter_cfg["format"] == LOGFMT_DEFAULT_FMT


@pytest.mark.json_extra
def test_python_json_logger_formatter_shape() -> None:
    from pythonjsonlogger.json import JsonFormatter

    logger = logging.getLogger("test_json_formatter")
    old_handlers = list(logger.handlers)
    old_level = logger.level
    old_propagate = logger.propagate
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    formatter = JsonFormatter("%(levelname)s %(name)s %(message)s %(asctime)s")
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    try:
        logger.info("hello %s", "world", extra={"user": "alice"})
    finally:
        logger.handlers = old_handlers
        logger.setLevel(old_level)
        logger.propagate = old_propagate

    payload = json.loads(stream.getvalue())
    assert payload["message"] == "hello world"
    assert payload["levelname"] == "INFO"
    assert payload["name"] == "test_json_formatter"
    assert payload["user"] == "alice"
    assert "asctime" in payload
