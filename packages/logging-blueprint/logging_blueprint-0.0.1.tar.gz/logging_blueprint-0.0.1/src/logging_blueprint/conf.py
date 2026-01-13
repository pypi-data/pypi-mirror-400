"""Core logging configuration utilities."""

from __future__ import annotations

import logging
import logging.config
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Final,
    Mapping,
    Sequence,
    cast,
)

from logging_blueprint.directives import parse_directives
from logging_blueprint.env import Env, parse_bool
from logging_blueprint.formatter.logfmt import LOGFMT_DEFAULT_FMT, LogfmtFormatter
from logging_blueprint.formatter.pretty import PrettyFormatter
from logging_blueprint.formatter.utils import require_python_json_logger
from logging_blueprint.styles import LogStyle, parse_style, resolve_style
from logging_blueprint.types import ensure_mutable_mapping

try:
    from typing import Self
except ImportError:  # pragma: no cover
    from typing_extensions import Self

DEFAULT_PY_LOG: Final = ""
DEFAULT_PY_LOG_FMT: Final = "%(asctime)s %(levelname)s %(name)s: %(message)s"
DEFAULT_PY_LOG_DATEFMT: Final = "%Y-%m-%d %H:%M:%S"
DEFAULT_PY_LOG_STREAM: Final = "stderr"


@dataclass(frozen=True, slots=True, kw_only=True)
class EnvLoggingConfig:
    """Rust-inspired env-driven logging configuration.

    Main knobs:
      - directives: Rust-like filter string (module=level, default level, comma-separated)
      - style: plain|pretty|logfmt|json|auto
      - stream: stdout|stderr (for the console handler)
      - fmt/datefmt: for plain/pretty/logfmt formatting
      - disable_existing_loggers: logging.dictConfig flag
    """

    directives: str
    style: LogStyle = LogStyle.AUTO
    stream: str = DEFAULT_PY_LOG_STREAM
    fmt: str = DEFAULT_PY_LOG_FMT
    datefmt: str = DEFAULT_PY_LOG_DATEFMT
    disable_existing_loggers: bool = False

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Self:
        """Create an EnvLoggingConfig from environment variables.

        This reads from os.environ by default, but you can also pass in a custom mapping.

        Args:
            env: Optional custom mapping of env vars to values. If None, we use os.environ.

        Returns:
            An EnvLoggingConfig object, populated with values from the environment.
        """
        directives = Env.PY_LOG.get("", env).strip()

        style_raw = Env.PY_LOG_STYLE.get("auto", env).strip().lower()
        style = parse_style(style_raw)

        stream = Env.PY_LOG_STREAM.get(DEFAULT_PY_LOG_STREAM, env).strip().lower()
        if stream not in ("stderr", "stdout"):
            raise ValueError(f"Invalid PY_LOG_STREAM value: {stream}")

        fmt = Env.PY_LOG_FMT.get(DEFAULT_PY_LOG_FMT, env)
        datefmt = Env.PY_LOG_DATEFMT.get(DEFAULT_PY_LOG_DATEFMT, env)

        disable_existing_raw = Env.PY_LOG_DISABLE_EXISTING.get("0", env)
        disable_existing = parse_bool(disable_existing_raw)

        return cls(
            directives=directives,
            style=style,
            stream=stream,
            fmt=fmt,
            datefmt=datefmt,
            disable_existing_loggers=disable_existing,
        )


def build_dict_config_from_env(
    env: EnvLoggingConfig | None = None,
    *,
    base: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a new dictConfig dict from env (optionally merging into a base config).

    - If base is provided, we copy it and overlay env choices.
    - Return type is Dict[str, Any] because logging's dictConfig schema is extensible.
    """
    if env is None:
        env = EnvLoggingConfig.from_env()

    if not base:
        base = {}

    merged = merge_env_into_dict_config(base, env)
    return merged


def merge_env_into_dict_config(
    config: Mapping[str, Any],
    env: EnvLoggingConfig | None = None,
) -> dict[str, Any]:
    """Merge env logging settings into an existing dictConfig-style mapping.

    This is the main "jumping off point" for:
      - YAML-derived dicts
      - arbitrary dict configs
      - programmatically built configs

    We return a new dict and do not mutate `config`.
    """
    if env is None:
        env = EnvLoggingConfig.from_env()

    style = resolve_style(env.style)

    # Start with a shallow copy for the top-level keys we touch.
    out: dict[str, Any] = dict(config)

    # Ensure baseline dictConfig structure exists.
    out.setdefault("version", 1)
    out["disable_existing_loggers"] = bool(env.disable_existing_loggers)

    formatters = ensure_mutable_mapping(out, "formatters")
    handlers = ensure_mutable_mapping(out, "handlers")
    loggers = ensure_mutable_mapping(out, "loggers")
    root = ensure_mutable_mapping(out, "root")

    # Install a default console handler + formatter, unless user already has something.
    # We use stable names so users can reference/override them in YAML.
    formatter_name: Final[str] = "envlog"
    handler_name: Final[str] = "envlog_console"

    if formatter_name not in formatters:
        formatters[formatter_name] = _make_formatter_dict(env, style)

    if handler_name not in handlers:
        handlers[handler_name] = _make_console_handler_dict(env, style, formatter_name)

    # Root logger: set level from directives default, install handler if none.
    directives = parse_directives(env.directives)
    default_level = directives.default_level_name or "INFO"

    root.setdefault("level", default_level)
    root_handlers = list(cast(Sequence[str], root.get("handlers", [])))
    if handler_name not in root_handlers:
        root_handlers.append(handler_name)
    root["handlers"] = root_handlers

    # Per-logger levels from directives
    for logger_name, level_name in directives.module_levels:
        entry = dict(cast(Mapping[str, Any], loggers.get(logger_name, {})))
        entry["level"] = level_name
        # By default, don't force handlers; allow user config to decide.
        loggers[logger_name] = cast(Any, entry)

    return out


def apply_env_logging(
    env: EnvLoggingConfig | None = None,
    *,
    base: Mapping[str, Any] | None = None,
) -> None:
    """One-liner: merge env config into base (if any) and call logging.config.dictConfig."""
    cfg = build_dict_config_from_env(env, base=base)
    logging.config.dictConfig(cfg)


def _make_formatter_dict(env: EnvLoggingConfig, style: LogStyle) -> dict[str, Any]:
    match style:
        case LogStyle.JSON:
            require_python_json_logger()
            return {
                "()": "pythonjsonlogger.json.JsonFormatter",
                "format": "%(levelname)s %(name)s %(message)s %(asctime)s",
            }
        case LogStyle.LOGFMT:
            fmt = env.fmt if env.fmt != DEFAULT_PY_LOG_FMT else LOGFMT_DEFAULT_FMT
            return {
                "()": f"{LogfmtFormatter.__module__}.{LogfmtFormatter.__qualname__}",
                "format": fmt,
                "datefmt": env.datefmt,
            }
        case LogStyle.PRETTY:
            return {
                "()": f"{PrettyFormatter.__module__}.{PrettyFormatter.__qualname__}",
                "format": env.fmt,
                "datefmt": env.datefmt,
            }
        case _:
            return {"format": env.fmt, "datefmt": env.datefmt}


def _make_console_handler_dict(env: EnvLoggingConfig, style: LogStyle, formatter_name: str) -> dict[str, Any]:
    stream_ref = "ext://sys.stdout" if env.stream == "stdout" else "ext://sys.stderr"
    base: Dict[str, Any] = {
        "class": "logging.StreamHandler",
        "level": "NOTSET",
        "formatter": formatter_name,
        "stream": stream_ref,
    }
    return base
