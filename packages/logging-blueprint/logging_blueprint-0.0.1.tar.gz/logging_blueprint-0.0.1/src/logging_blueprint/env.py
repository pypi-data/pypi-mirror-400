"""Environment variable processing."""

import os
from collections.abc import Mapping
from enum import Enum
from typing import overload


class Env(str, Enum):
    """Well-known environment variable keys."""

    PY_LOG = "PY_LOG"
    PY_LOG_FMT = "PY_LOG_FMT"
    PY_LOG_DATEFMT = "PY_LOG_DATEFMT"
    PY_LOG_STREAM = "PY_LOG_STREAM"
    PY_LOG_STYLE = "PY_LOG_STYLE"
    PY_LOG_DISABLE_EXISTING = "PY_LOG_DISABLE_EXISTING"

    @overload
    def get(self, default: str, /, env: Mapping[str, str] | None = None) -> str: ...

    @overload
    def get(self, default: str | None = None, /, env: Mapping[str, str] | None = None) -> str | None: ...

    def get(self, default: str | None = None, /, env: Mapping[str, str] | None = None) -> str | None:
        """Retrieve the value of the environment variable.

        Args:
            default: Default value to return if the environment variable is not set.
            env: Environment variables mapping to use instead of `os.environ`. This is useful for testing.

        Returns:
            The value of the environment variable, or the default value if it is not set.
        """
        if env is not None:
            return env.get(self.value, default)

        return os.environ.get(self.value, default)


def parse_bool(s: str) -> bool:
    """Parse a string as a boolean value.

    It's assumed that this string was sourced from an environment variable, so it's trimmed and lowercased before
    parsing.

    Examples:
        >>> parse_bool("1")
        True
        >>> parse_bool("true")
        True
        >>> parse_bool("false")
        False
    """
    return s.strip().lower() in {"1", "true", "yes", "y", "on"}
