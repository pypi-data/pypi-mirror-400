from __future__ import annotations

from pathlib import Path

import pytest

from screenshot._models_options import ScreenshotOptions
from screenshot._shared.options_normalizer import (
    _normalize_viewports,
    ensure_capture_enabled,
    ensure_sequence_lists,
    normalize_options_payload,
)


def test_normalize_options_payload_flat_schema() -> None:
    raw = {
        "enabled": True,
        "max_pages": 3,
        "depth": 1,
        "viewports": ("desktop", "mobile"),
        "delay": 0.5,
        "timeout": 10.0,
        "allow_autoplay": False,
        "block_media": True,
        "playwright_executable_path": "/opt/chrome",
        "extra": {"feature": "on"},
        "schema_version": "ignored-here",
    }

    normalized = normalize_options_payload(raw)

    assert normalized["capture"]["enabled"] is True
    assert normalized["capture"]["post_nav_wait_s"] == 0.5
    assert normalized["capture"]["timeout_s"] == 10.0
    assert normalized["capture"]["viewports"] == ["desktop", "mobile"]
    assert normalized["browser"]["block_media"] is True
    assert normalized["browser"]["allow_autoplay"] is False
    assert normalized["runner"]["playwright_executable_path"] == "/opt/chrome"
    assert normalized["runner"]["extra"] == {"feature": "on"}


def test_normalize_options_payload_nested_copy_safe() -> None:
    raw = {"capture": {"viewports": ["desktop"]}}
    normalized = normalize_options_payload(raw)

    assert normalized["capture"]["viewports"] == ["desktop"]
    assert normalized is not raw
    assert normalized["capture"] is not raw["capture"]
    normalized["capture"]["viewports"].append("tablet")
    assert raw["capture"]["viewports"] == ["desktop"]


def test_normalize_viewports_favors_non_empty_entries() -> None:
    assert _normalize_viewports(None) == []
    assert _normalize_viewports(" mobile ") == ["mobile"]
    assert _normalize_viewports({"name": "custom"}) == [{"name": "custom"}]
    assert _normalize_viewports({"key": "value"}) == [{"key": "value"}]
    assert _normalize_viewports({"name": None}) == [{"name": None}]
    assert _normalize_viewports(["desktop", None, "mobile"]) == ["desktop", "mobile"]


def test_ensure_capture_enabled_and_sequence_lists() -> None:
    options = ScreenshotOptions.from_dict({"capture": {"enabled": False}})
    enabled = ensure_capture_enabled(options)
    assert enabled.capture.enabled is True
    assert options.capture.enabled is False

    expanded = ScreenshotOptions.from_dict(
        {
            "capture": {"enabled": True, "viewports": ["desktop", "mobile"]},
            "runner": {
                "extra_styles": ["body { color: red; }"],
                "extra_init_scripts": ["console.log('init')"],
                "extra": {"trace": True},
                "playwright_executable_path": Path("/usr/bin/chrome"),
            },
        }
    )
    flattened = ensure_sequence_lists(expanded)
    assert flattened.capture.viewports == ("desktop", "mobile")
    assert list(flattened.runner.extra_styles) == ["body { color: red; }"]
    assert list(flattened.runner.extra_init_scripts) == ["console.log('init')"]
    assert flattened.runner.extra["trace"] is True
    assert flattened.runner.playwright_executable_path == str(Path("/usr/bin/chrome"))


def test_schema_version_passthrough() -> None:
    with pytest.raises(ValueError):
        ScreenshotOptions.from_dict({"schema_version": "unexpected"})

    valid = ScreenshotOptions.from_dict({"capture": {"enabled": True}})
    assert valid.to_dict()["schema_version"] == "screenshot_options/v2"
