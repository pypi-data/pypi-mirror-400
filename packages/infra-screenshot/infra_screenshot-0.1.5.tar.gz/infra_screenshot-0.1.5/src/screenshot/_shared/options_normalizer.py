"""Normalize screenshot option payloads for services and tooling.

This module centralises the legacy-input handling that previously lived in the
Azure Function layer and the coordinator CLI.  Upstream callers often provide
"flat" dictionaries that predate the nested schema introduced in
``ScreenshotOptions``.  The helpers below lift those payloads into the modern
structure, guarantee list-based sequences for JSON round-tripping, and expose a
safe way to flip the capture toggle on frozen dataclasses.

Example:
    >>> from screenshot.models import ScreenshotOptions
    >>> raw = {"enabled": True, "max_pages": 3, "viewports": ["desktop"]}
    >>> normalized = normalize_options_payload(raw)
    >>> options = ScreenshotOptions.from_dict(normalized)
    >>> ensure_capture_enabled(options).capture.enabled
    True
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from copy import deepcopy
from dataclasses import replace
from typing import Any

from ..models import ScreenshotOptions

_FLAT_SECTION_KEYS = ("capture", "browser", "runner")


def normalize_options_payload(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Convert legacy flat option dictionaries into the nested schema.

    The function leaves already-nested payloads untouched (aside from copying
    them) to make sure callers can mutate the result without impacting the
    original.  Flat inputs are split into the ``capture``/``browser``/``runner``
    sections expected by :meth:`ScreenshotOptions.from_dict`.

    Args:
        raw: User-provided payload that may follow the legacy flat schema.

    Returns:
        A dictionary compatible with :meth:`ScreenshotOptions.from_dict`.
    """

    if any(key in raw for key in _FLAT_SECTION_KEYS):
        normalized_payload = deepcopy(dict(raw))
        capture_section = normalized_payload.get("capture")
        if isinstance(capture_section, MutableMapping):
            capture_section["viewports"] = _normalize_viewports(capture_section.get("viewports"))
        return normalized_payload

    capture: dict[str, Any] = {}
    browser: dict[str, Any] = {}
    runner: dict[str, Any] = {}

    _copy_field(raw, capture, "enabled")
    _copy_field(raw, capture, "max_pages")
    _copy_field(raw, capture, "depth")
    if "viewports" in raw:
        capture["viewports"] = _normalize_viewports(raw.get("viewports"))
    _copy_field(raw, capture, "post_nav_wait_s", aliases=("delay", "post_nav_wait"))
    _copy_field(raw, capture, "timeout_s", aliases=("timeout",))
    _copy_field(raw, capture, "max_total_duration_s", aliases=("max_total_duration",))
    _copy_field(raw, capture, "max_capture_attempts")
    _copy_field(raw, capture, "max_viewport_concurrency")
    _copy_field(raw, capture, "scroll")
    _copy_field(raw, capture, "scroll_step_delay_ms", aliases=("scroll_step_delay",))
    _copy_field(raw, capture, "max_scroll_steps", aliases=("scroll_steps",))
    _copy_field(raw, capture, "full_page")
    _copy_field(raw, capture, "pre_capture_wait_s", aliases=("settle_timeout",))

    _copy_field(raw, browser, "allow_autoplay")
    _copy_field(raw, browser, "hide_overlays")
    _copy_field(raw, browser, "reduced_motion")
    _copy_field(raw, browser, "disable_animations")
    _copy_field(raw, browser, "mute_media")
    _copy_field(raw, browser, "block_media")
    _copy_field(raw, browser, "compatibility_level")
    _copy_field(raw, browser, "user_agent")

    _copy_field(raw, runner, "extra_styles")
    _copy_field(raw, runner, "extra_init_scripts")
    _copy_field(
        raw,
        runner,
        "playwright_executable_path",
        aliases=("chromium_path", "browser_path", "playwright_path"),
    )
    extra_payload = raw.get("extra")
    if isinstance(extra_payload, Mapping):
        runner["extra"] = dict(extra_payload)

    normalized: dict[str, Any] = {}
    if capture:
        normalized["capture"] = capture
    if browser:
        normalized["browser"] = browser
    if runner:
        normalized["runner"] = runner

    schema_version = raw.get("schema_version")
    if schema_version is not None:
        normalized["schema_version"] = schema_version

    return normalized if normalized else {"capture": {"enabled": True}}


def ensure_capture_enabled(options: ScreenshotOptions) -> ScreenshotOptions:
    """Return a copy of ``options`` with capture forcibly enabled."""

    if options.capture.enabled:
        return options
    return replace(options, capture=replace(options.capture, enabled=True))


def ensure_sequence_lists(options: ScreenshotOptions) -> ScreenshotOptions:
    """Return a copy with sequence fields converted to plain lists.

    ``asdict`` prefers list objects for stable JSON output, while most of the
    core models use tuples for immutability.  This helper keeps the internal
    dataclass frozen while presenting a list-based view of the relevant
    sequences.
    """

    capture_viewports = list(options.capture.viewports)
    updated_capture = replace(options.capture, viewports=tuple(capture_viewports))

    runner = options.runner
    updated_runner = replace(
        runner,
        extra_styles=tuple(runner.extra_styles),
        extra_init_scripts=tuple(runner.extra_init_scripts),
        extra=dict(runner.extra),
    )

    return replace(options, capture=updated_capture, runner=updated_runner)


def _copy_field(
    source: Mapping[str, Any],
    target: MutableMapping[str, Any],
    key: str,
    *,
    aliases: tuple[str, ...] = (),
) -> None:
    for candidate in (key, *aliases):
        if candidate in source:
            target[key] = source[candidate]
            return


def _normalize_viewports(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, Mapping):
        return [dict(value)]
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if isinstance(value, list | tuple | set | frozenset):
        return [item for item in value if item is not None]
    return [value]


__all__ = [
    "normalize_options_payload",
    "ensure_capture_enabled",
    "ensure_sequence_lists",
]
