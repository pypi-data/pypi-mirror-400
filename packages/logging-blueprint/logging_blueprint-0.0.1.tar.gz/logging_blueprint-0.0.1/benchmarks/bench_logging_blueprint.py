"""Microbenchmarks for logging-blueprint initialization and formatter usage."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

import pyperf  # type: ignore[import-untyped]

from logging_blueprint import EnvLoggingConfig, apply_env_logging
from logging_blueprint.formatter.logfmt import LOGFMT_DEFAULT_FMT, LogfmtFormatter
from logging_blueprint.formatter.pretty import PrettyFormatter
from logging_blueprint.styles import LogStyle

DEFAULT_PLAIN_FMT: Final = "%(asctime)s %(levelname)s %(name)s: %(message)s"
DEFAULT_DATEFMT: Final = "%Y-%m-%d %H:%M:%S"
JSON_FMT: Final = "%(levelname)s %(name)s %(message)s %(asctime)s"


class FormattingHandler(logging.Handler):
    def __init__(self, formatter: logging.Formatter) -> None:
        super().__init__()
        self.setFormatter(formatter)

    def emit(self, record: logging.LogRecord) -> None:
        _ = self.format(record)


@dataclass(frozen=True, slots=True)
class BenchStyle:
    name: str
    style: LogStyle
    fmt: str
    datefmt: str
    formatter_factory: Callable[[str, str], logging.Formatter]


def _json_formatter_factory(fmt: str, _datefmt: str) -> logging.Formatter:
    from pythonjsonlogger.json import JsonFormatter

    return JsonFormatter(fmt)


def _json_available() -> bool:
    try:
        from pythonjsonlogger import json as _json_module
    except ImportError:
        return False
    else:
        return _json_module is not None


def _styles() -> list[BenchStyle]:
    styles = [
        BenchStyle(
            name="plain",
            style=LogStyle.PLAIN,
            fmt=DEFAULT_PLAIN_FMT,
            datefmt=DEFAULT_DATEFMT,
            formatter_factory=logging.Formatter,
        ),
        BenchStyle(
            name="pretty",
            style=LogStyle.PRETTY,
            fmt=DEFAULT_PLAIN_FMT,
            datefmt=DEFAULT_DATEFMT,
            formatter_factory=PrettyFormatter,
        ),
        BenchStyle(
            name="logfmt",
            style=LogStyle.LOGFMT,
            fmt=LOGFMT_DEFAULT_FMT,
            datefmt=DEFAULT_DATEFMT,
            formatter_factory=LogfmtFormatter,
        ),
    ]
    if _json_available():
        styles.append(
            BenchStyle(
                name="json",
                style=LogStyle.JSON,
                fmt=JSON_FMT,
                datefmt=DEFAULT_DATEFMT,
                formatter_factory=_json_formatter_factory,
            )
        )
    return styles


def _make_record() -> logging.LogRecord:
    record = logging.LogRecord(
        name="bench",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )
    record.user = "alice"
    record.request_id = "req-123"
    return record


def _bench_init(env: EnvLoggingConfig) -> Callable[[int], float]:
    def run(loops: int) -> float:
        start = time.perf_counter()
        for _ in range(loops):
            apply_env_logging(env)
        elapsed = time.perf_counter() - start
        logging.shutdown()
        return elapsed

    return run


def _bench_formatter(formatter: logging.Formatter) -> Callable[[int], float]:
    record = _make_record()

    def run(loops: int) -> float:
        start = time.perf_counter()
        for _ in range(loops):
            formatter.format(record)
        return time.perf_counter() - start

    return run


def _bench_logger(formatter: logging.Formatter) -> Callable[[int], float]:
    def run(loops: int) -> float:
        logger = logging.getLogger("bench.logger")
        old_handlers = list(logger.handlers)
        old_level = logger.level
        old_propagate = logger.propagate
        handler = FormattingHandler(formatter)
        logger.handlers = [handler]
        logger.setLevel(logging.INFO)
        logger.propagate = False

        try:
            start = time.perf_counter()
            for i in range(loops):
                logger.info("hello %s", "world", extra={"user": "alice", "request_id": i})
            return time.perf_counter() - start
        finally:
            logger.handlers = old_handlers
            logger.setLevel(old_level)
            logger.propagate = old_propagate
            handler.close()

    return run


def main() -> None:
    runner = pyperf.Runner()

    for style in _styles():
        env = EnvLoggingConfig(
            directives="info",
            style=style.style,
            stream="stderr",
            fmt=style.fmt,
            datefmt=style.datefmt,
        )
        runner.bench_time_func(f"init_{style.name}", _bench_init(env))

        formatter = style.formatter_factory(style.fmt, style.datefmt)
        runner.bench_time_func(f"formatter_{style.name}", _bench_formatter(formatter))

        logger_formatter = style.formatter_factory(style.fmt, style.datefmt)
        runner.bench_time_func(f"logger_{style.name}", _bench_logger(logger_formatter))


if __name__ == "__main__":
    main()
