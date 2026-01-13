"""Style-related utilities for logging-blueprint."""

import logging
import os
import sys
from enum import Enum

logger = logging.getLogger(__name__)


class LogStyle(str, Enum):
    """Enumeration of logging styles supported by this module."""

    #: Plain text, no colors or JSON.
    PLAIN = "plain"
    #: Colored output, for human-friendly console output.
    PRETTY = "pretty"
    #: Logfmt key=value output, human-friendly and parsable.
    LOGFMT = "logfmt"
    #: Structured JSON output, for machine-friendly logging.
    JSON = "json"
    #: Automatically choose style based on environment.
    AUTO = "auto"


def parse_style(s: str) -> LogStyle:
    """Parse a LogStyle name string into a LogStyle enum value.

    Examples:
        >>> parse_style("plain")
        <LogStyle.PLAIN: 'plain'>
        >>> parse_style("pretty")
        <LogStyle.PRETTY: 'pretty'>
    """
    normalized = s.strip().lower()
    aliases = {"color": LogStyle.PRETTY}
    if normalized in aliases:
        return aliases[normalized]

    try:
        return LogStyle(normalized)
    except ValueError:
        logger.error("Unrecognized log style %r, defaulting to AUTO", normalized)
        return LogStyle.AUTO


def resolve_style(style: LogStyle) -> LogStyle:
    """Resolve the provided log style, defaulting to a reasonable value if AUTO is provided.

    This function implements the heuristics used to determine the appropriate log style when AUTO is provided.

    The current heuristics are:
    - Prefer JSON when running in k8s.
    - Prefer JSON when stdout and stderr are not TTYs.
    - Otherwise, prefer 'pretty'.

    Args:
        style: The log style to resolve.

    Returns:
        The resolved log style, which will never be AUTO.
    """
    if style is not LogStyle.AUTO:
        return style

    # AUTO heuristic: prefer JSON when running in k8s or when stdout is not a TTY.
    if "KUBERNETES_SERVICE_HOST" in os.environ:
        return LogStyle.JSON
    if not sys.stderr.isatty() and not sys.stdout.isatty():
        return LogStyle.JSON
    return LogStyle.PRETTY
