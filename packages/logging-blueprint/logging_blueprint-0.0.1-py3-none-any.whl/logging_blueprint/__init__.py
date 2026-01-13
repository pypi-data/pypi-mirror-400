"""Environment-driven configuration for Python’s standard library logging module.

This is the root of the `logging-blueprint` package.

NOTE: This package is **EXPERIMENTAL** and breaking changes should be expected, even to "public" interfaces.
Contributors are welcome to make _justifiable_ breaking changes to the package as-needed.
"""

from __future__ import annotations

from logging_blueprint.conf import (
    EnvLoggingConfig,
    apply_env_logging,
    build_dict_config_from_env,
    merge_env_into_dict_config,
)
from logging_blueprint.styles import LogStyle

# Module-level re-exports
# These serve to provide a simple, consistent API for the package.
__all__ = (
    "apply_env_logging",
    "build_dict_config_from_env",
    "EnvLoggingConfig",
    "LogStyle",
    "merge_env_into_dict_config",
)
