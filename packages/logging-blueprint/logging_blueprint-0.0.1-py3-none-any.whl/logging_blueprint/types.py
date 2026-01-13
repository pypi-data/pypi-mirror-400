"""Typing for various data structures."""

from __future__ import annotations

from typing import (
    Any,
    MutableMapping,
)


def ensure_mutable_mapping(d: dict[str, Any], key: str) -> MutableMapping[str, Any]:
    """Given a dict `d`, ensure it has a mutable mapping at key `key`.

    Args:
        d: A dict to modify in place.
        key: A key in `d` that should be a dict or mapping.
            If not, we create one.
            If it's not a dict, we copy to a new dict.

    Returns:
        The dict or mapping at `d[key]`, which is guaranteed to be mutable.
    """
    v = d.get(key)
    if v is None:
        m: dict[str, Any] = {}
        d[key] = m
        return m
    if isinstance(v, dict):
        m2 = dict(v)
        d[key] = m2
        return m2

    # If user passed a non-dict mapping, copy to dict.
    m2 = dict(v)
    d[key] = m2
    return m2
