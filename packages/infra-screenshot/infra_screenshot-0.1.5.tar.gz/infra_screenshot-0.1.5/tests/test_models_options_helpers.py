from __future__ import annotations

from pathlib import Path

import pytest

from screenshot._models_options import (
    OPTIONS_SCHEMA_VERSION,
    CaptureOptions,
    ScreenshotOptions,
    _capture_from_nested_dict,
    _capture_to_dict,
    _runner_from_nested_dict,
    _to_int,
)


def test_capture_options_validation_and_merge() -> None:
    defaults = {"desktop": {"viewport": {"width": 800, "height": 600}}}
    options = CaptureOptions(enabled=True, viewports=("desktop", {"name": "custom"}))
    merged = options.merged_viewports(defaults)

    assert merged["desktop"]["viewport"]["width"] == 800
    assert "custom" in merged

    with pytest.raises(ValueError):
        CaptureOptions(max_pages=0)
    with pytest.raises(TypeError):
        CaptureOptions(viewports=("desktop", 123))  # type: ignore[arg-type]


def test_capture_from_dict_and_round_trip() -> None:
    capture = _capture_from_nested_dict(
        {
            "enabled": True,
            "max_pages": "2",
            "depth": "1",
            "viewports": ["mobile"],
            "post_nav_wait_s": "1.25",
            "timeout_s": "30",
            "max_total_duration_s": "0",
            "max_capture_attempts": "4",
            "max_viewport_concurrency": "3",
            "scroll": True,
            "scroll_step_delay_ms": "120",
            "max_scroll_steps": "5",
            "full_page": True,
            "pre_capture_wait_s": "0.75",
        }
    )
    as_dict = _capture_to_dict(capture)
    assert as_dict["max_pages"] == 2
    assert as_dict["depth"] == 1
    assert as_dict["viewports"] == ["mobile"]
    assert as_dict["max_total_duration_s"] is None
    assert as_dict["pre_capture_wait_s"] == 0.75
    assert as_dict["scroll_step_delay_ms"] == 120
    assert as_dict["max_scroll_steps"] == 5


def test_runner_from_nested_dict_coerces_types() -> None:
    runner = _runner_from_nested_dict(
        {
            "extra_styles": ["a"],
            "extra_init_scripts": ("b",),
            "playwright_executable_path": Path("/tmp/chrome"),
            "extra": {"feature": "on"},
        }
    )

    assert runner.playwright_executable_path == str(Path("/tmp/chrome"))
    assert runner.extra_styles == ("a",)
    assert runner.extra["feature"] == "on"


def test_screenshot_options_schema_and_serialization() -> None:
    opts = ScreenshotOptions.from_dict({"capture": {"enabled": True}})
    payload = opts.to_dict()
    assert payload["schema_version"] == OPTIONS_SCHEMA_VERSION
    assert payload["capture"]["enabled"] is True

    with pytest.raises(ValueError):
        ScreenshotOptions.from_dict({})


def test_to_int_accepts_bool() -> None:
    assert _to_int(True, default=0) == 1
