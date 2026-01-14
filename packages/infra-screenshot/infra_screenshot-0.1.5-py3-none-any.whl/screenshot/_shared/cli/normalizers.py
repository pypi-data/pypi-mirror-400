"""Shared normalisation helpers used by CLI option builders."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

__all__ = [
    "_ensure_list",
    "_pick",
    "_to_float",
    "_bool_field",
    "_numeric_field",
]


def _ensure_list(value: object | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list | tuple | set):
        return [str(item) for item in value if isinstance(item, str)]
    return [str(value)]


def _pick(containers: Sequence[dict[str, object]], *keys: str) -> object | None:
    for key in keys:
        for container in containers:
            if not isinstance(container, dict):
                continue
            if key in container and container[key] is not None:
                return container[key]
    return None


def _to_float(value: object | None, default: float) -> float:
    """Best-effort conversion to float for loosely-typed CLI inputs.

    Returns the provided default when value is None or cannot be coerced.
    """
    if value is None:
        return default
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


def _bool_field(
    containers: Sequence[dict[str, object]],
    keys: Sequence[str],
    arg_value: bool | None,
    default: bool,
) -> bool:
    raw = _pick(containers, *keys)
    if raw is not None:
        return bool(raw)
    if arg_value is not None:
        return bool(arg_value)
    return default


def _numeric_field(
    containers: Sequence[dict[str, object]],
    keys: Sequence[str],
    *,
    fallback: object | None,
    default: float,
    coerce: Callable[[Any], float],
    minimum: float | None = None,
) -> float:
    raw = _pick(containers, *keys)
    if raw is None:
        raw = fallback
    if raw is None:
        raw = default
    value = coerce(raw)
    if minimum is not None:
        value = max(minimum, value)
    return value
