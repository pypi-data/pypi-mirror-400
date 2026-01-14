"""Validation helpers for CLI options materialization inputs.

Current responsibilities:
- Validate the `schema_version` field on overrides/nested payloads.
  Returns the normalized schema string or `None` if not provided; raises
  a `ValueError` when the version does not match the expected constant.

Keep logic here small and reusable so `options.py` can remain a thin facade.
"""

from __future__ import annotations

from collections.abc import Mapping

from ..._models_options import OPTIONS_SCHEMA_VERSION


def validate_schema_version(data: Mapping[str, object]) -> str | None:
    """Validate the provided schema_version if present.

    Returns the normalized schema string when provided, otherwise None.
    Raises ValueError when the version does not match the expected constant.
    """
    schema_version = data.get("schema_version")
    if schema_version is None:
        return None
    normalized = str(schema_version).strip()
    if normalized != OPTIONS_SCHEMA_VERSION:
        expected = OPTIONS_SCHEMA_VERSION
        version = normalized or "unknown"
        raise ValueError(f"Unsupported screenshot options schema '{version}'; expected {expected}")
    return normalized
