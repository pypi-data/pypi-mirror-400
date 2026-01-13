"""Directive parsing logic.

This module takes comma-separated logging directives, like "info,myapp.db=debug,urllib3=warning",
and parses it into a structured form.
"""

from __future__ import annotations

import logging
from typing import NamedTuple


class ParsedDirectives(NamedTuple):
    """Parsed form of directives.

    - default_level_name: e.g. "INFO"
    - module_levels: list of ("pkg.sub", "DEBUG")
    """

    default_level_name: str | None
    module_levels: tuple[tuple[str, str], ...]


def parse_directives(directives: str) -> ParsedDirectives:
    """Parse "info,myapp.db=debug,urllib3=warning" like env_logger.

    Rules:
      - Comma-separated directives
      - Each directive is either:
          level
          module=level
      - First bare "level" becomes the default root level (last bare wins)
    """
    default_level: str | None = None
    module_levels: list[tuple[str, str]] = []

    for raw in directives.split(","):
        item = raw.strip()
        if not item:
            continue

        if "=" in item:
            mod, lvl = item.split("=", 1)
            mod = mod.strip()
            lvl_name = _normalize_level_name(lvl.strip())
            if mod:
                module_levels.append((mod, lvl_name))
        else:
            default_level = _normalize_level_name(item)

    return ParsedDirectives(default_level_name=default_level, module_levels=tuple(module_levels))


def _normalize_level_name(raw: str) -> str:
    x = raw.strip().upper()
    aliases: dict[str, str] = {
        "WARN": "WARNING",
        "ERR": "ERROR",
        "CRIT": "CRITICAL",
        "FATAL": "CRITICAL",
        "TRACE": "DEBUG",  # stdlib doesn't have TRACE by default
    }
    x = aliases.get(x, x)
    # Validate, fall back to INFO
    if logging.getLevelName(x) == f"Level {x}":  # unknown string
        return "INFO"
    return x
