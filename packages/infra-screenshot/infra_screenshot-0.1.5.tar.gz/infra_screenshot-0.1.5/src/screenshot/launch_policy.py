"""Centralised Chromium launch policy for screenshot capture."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

FORGIVENESS_LEVELS: Sequence[str] = ("low", "medium", "high")

_BASE_FLAGS: list[str] = [
    "--disable-dev-shm-usage",
    "--disable-extensions",
    "--disable-component-update",
    "--disable-gpu",
    "--use-angle=swiftshader",
    "--force-color-profile=srgb",
]

_MEDIUM_FLAGS: list[str] = [
    "--allow-running-insecure-content",
    "--disable-features=IsolateOrigins,site-per-process",
]

_HIGH_FLAGS: list[str] = [
    "--ignore-certificate-errors",
    "--ignore-ssl-errors",
    "--ignore-certificate-errors-spki-list",
    "--disable-web-security",
    "--no-sandbox",
    "--disable-setuid-sandbox",
]


def normalise_level(level: str) -> str:
    """Normalise forgiveness level input and validate the choice."""

    value = (level or "low").strip().lower()
    if value not in FORGIVENESS_LEVELS:
        raise ValueError(
            f"Unknown forgiveness level '{level}'; expected one of {FORGIVENESS_LEVELS}"
        )
    return value


def build_chromium_args(
    level: str,
    *,
    extra_args: Iterable[str] | None = None,
    skip_args: Iterable[str] | None = None,
) -> list[str]:
    """Return Chromium launch arguments for the requested forgiveness level.

    Args:
        level: One of ``\"low\"``, ``\"medium\"`` or ``\"high\"`` (case-insensitive).
        extra_args: Additional flags to append (used by experiments/tests).
        skip_args: Flags to remove from the computed set for one-off overrides.

    Returns:
        Ordered list of unique Chromium CLI flags.

    Example:
        >>> build_chromium_args(\"low\")[:2]
        ['--disable-dev-shm-usage', '--disable-extensions']
    """

    value = normalise_level(level)
    flags: list[str] = list(_BASE_FLAGS)
    if value in ("medium", "high"):
        flags.extend(_MEDIUM_FLAGS)
    if value == "high":
        flags.extend(_HIGH_FLAGS)

    if extra_args:
        flags.extend(extra_args)

    if skip_args:
        to_skip = set(skip_args)
        flags = [flag for flag in flags if flag not in to_skip]

    # Preserve order but drop duplicates
    seen = set()
    unique_flags: list[str] = []
    for flag in flags:
        if flag not in seen:
            unique_flags.append(flag)
            seen.add(flag)
    return unique_flags


def describe_levels() -> dict[str, list[str]]:
    """Return the launch flags associated with each forgiveness level."""

    return {
        "low": list(_BASE_FLAGS),
        "medium": list(_BASE_FLAGS + _MEDIUM_FLAGS),
        "high": list(_BASE_FLAGS + _MEDIUM_FLAGS + _HIGH_FLAGS),
    }
