from pathlib import Path
from typing import Any

import pytest

from screenshot import ScreenshotBatchResult, ScreenshotCaptureResult, ScreenshotOptions
from screenshot._models_options import OPTIONS_SCHEMA_VERSION, CaptureOptions
from screenshot._shared.errors import make_error


def test_screenshot_options_merged_viewports() -> None:
    defaults = {
        "desktop": {
            "viewport": {"width": 1280, "height": 720},
            "device_scale_factor": 1.0,
            "is_mobile": False,
            "has_touch": False,
        },
        "mobile": {
            "viewport": {"width": 390, "height": 844},
            "device_scale_factor": 2.5,
            "is_mobile": True,
            "has_touch": True,
        },
    }
    options = ScreenshotOptions(
        capture=CaptureOptions(
            viewports=(
                "desktop",
                {
                    "name": "custom",
                    "viewport": {"width": 800, "height": 600},
                    "device_scale_factor": 1.5,
                    "is_mobile": False,
                },
                {},
                "unknown",
            )
        )
    )

    merged: dict[str, dict[str, Any]] = options.capture.merged_viewports(defaults)

    assert "desktop" in merged
    assert merged["desktop"]["viewport"]["width"] == 1280
    assert merged["custom"]["viewport"]["height"] == 600
    assert "unknown" not in merged


def test_screenshot_capture_result_succeeded_logic(tmp_path: Path) -> None:
    success = ScreenshotCaptureResult(
        requested=0,
        captured=0,
        failed=0,
        metadata_path=tmp_path / "meta.json",
        errors=[],
        job_id="job-1",
    )
    failure = ScreenshotCaptureResult(
        requested=1,
        captured=0,
        failed=1,
        metadata_path=None,
        errors=[make_error("runtime", "error")],
        job_id="job-2",
    )

    assert success.succeeded is True
    assert failure.succeeded is False


def test_screenshot_batch_result_serialization(tmp_path: Path) -> None:
    results = [
        ScreenshotCaptureResult(
            requested=1,
            captured=1,
            failed=0,
            metadata_path=tmp_path / "meta.json",
            errors=[],
            job_id="job-1",
        ),
        ScreenshotCaptureResult(
            requested=1,
            captured=0,
            failed=1,
            metadata_path=None,
            errors=[make_error("runtime", "failure")],
            job_id="job-2",
        ),
    ]
    batch = ScreenshotBatchResult(results=results)

    assert len(batch.successes) == 1
    assert len(batch.failures) == 1

    payload: dict[str, Any] = batch.to_dict()
    assert payload["success_count"] == 1
    assert payload["failure_count"] == 1
    assert payload["results"][1]["errors"][0]["message"] == "failure"
    assert payload["results"][1]["errors"][0]["error_type"] == "runtime"


def test_capture_result_error_messages_property(tmp_path: Path) -> None:
    error = make_error("timeout", "took too long", retryable=True)
    result = ScreenshotCaptureResult(
        requested=1,
        captured=0,
        failed=1,
        metadata_path=None,
        entries=[],
        errors=[error],
        job_id="job-42",
    )

    assert result.error_messages == ["took too long"]


def test_screenshot_options_from_dict_validates_schema() -> None:
    with pytest.raises(ValueError, match="Expected schema"):
        ScreenshotOptions.from_dict({"schema_version": "screenshot_options/v1", "capture": {}})


def test_screenshot_options_from_dict_requires_sections() -> None:
    with pytest.raises(ValueError, match="expects at least one"):
        ScreenshotOptions.from_dict({"schema_version": OPTIONS_SCHEMA_VERSION})


def test_screenshot_options_from_dict_accepts_nested_schema() -> None:
    options = ScreenshotOptions.from_dict(
        {
            "schema_version": OPTIONS_SCHEMA_VERSION,
            "capture": {
                "enabled": True,
                "max_pages": 2,
                "viewports": ["desktop", "mobile"],
            },
            "browser": {
                "allow_autoplay": False,
                "hide_overlays": False,
                "compatibility_level": "medium",
            },
            "runner": {
                "extra_styles": ["body { color: green; }"],
                "extra_init_scripts": ["console.log('nested')"],
            },
        }
    )

    assert options.capture.enabled is True
    assert options.capture.max_pages == 2
    assert options.capture.viewports == ("desktop", "mobile")
    assert options.browser.allow_autoplay is False
    assert options.browser.hide_overlays is False
    assert options.browser.compatibility_level == "medium"
    assert options.runner.extra_styles == ("body { color: green; }",)
    assert options.runner.extra_init_scripts == ("console.log('nested')",)
