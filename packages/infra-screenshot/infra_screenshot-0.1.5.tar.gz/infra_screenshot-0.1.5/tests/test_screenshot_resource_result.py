from __future__ import annotations

from test_utils import create_capture_result

from screenshot import ScreenshotCaptureResult, ScreenshotResourceOutcome
from screenshot._internal import from_capture_result, per_viewport_resources
from screenshot._shared.errors import ScreenshotError


def test_from_capture_result_success_metadata_and_config_normalization() -> None:
    capture = create_capture_result(requested=2, captured=2, failed=0)

    config_a = {
        "viewports": ["desktop", "mobile"],
        "depth": 1,
        "timeout_s": 45.0,
        "scroll": True,
        "full_page": False,
    }
    config_b = {
        "viewports": ["mobile", "desktop"],  # different order but equivalent
        "depth": 1,
        "timeout_s": 45.0,
        "scroll": True,
        "full_page": False,
        "ignored": "value",
    }

    result_a = from_capture_result(
        capture,
        resource_key="screenshots",
        config=config_a,
    )
    result_b = from_capture_result(
        capture,
        resource_key="screenshots",
        config=config_b,
    )

    assert result_a.outcome is ScreenshotResourceOutcome.SUCCESS
    assert result_a.errors == []
    assert result_a.metadata["requested"] == 2
    assert result_a.metadata["captured"] == 2
    assert result_a.metadata["job_id"] == "job-123"
    assert result_a.metadata["metadata_path"].endswith("meta.json")
    assert result_a.config_key == result_b.config_key


def test_from_capture_result_failure_and_error_categorization() -> None:
    capture = create_capture_result(
        requested=1,
        captured=0,
        failed=1,
        errors=[
            ScreenshotError(error_type="TimeoutError", message="took too long", retryable=True),
            ScreenshotError(error_type="NavigationCrash", message="nav failed"),
        ],
    )

    result = from_capture_result(
        capture,
        resource_key="screenshots.desktop",
        config={"viewports": ["desktop"]},
    )

    assert result.outcome is ScreenshotResourceOutcome.FAILED
    assert [err.category for err in result.errors] == [
        "screenshot.timeout",
        "screenshot.navigation",
    ]
    assert result.errors[0].retryable is True


def test_from_capture_result_partial_and_custom_metadata() -> None:
    capture = create_capture_result(requested=3, captured=2, failed=1)

    result = from_capture_result(
        capture,
        resource_key="screenshots.bundle",
        config={"viewports": ["desktop", "tablet"]},
        metadata={"extra": "value"},
    )

    assert result.outcome is ScreenshotResourceOutcome.PARTIAL
    assert result.metadata["extra"] == "value"


def test_from_capture_result_skipped_when_no_requests() -> None:
    capture = create_capture_result(requested=0, captured=0, failed=0)

    result = from_capture_result(
        capture,
        resource_key="screenshots",
        config={"viewports": []},
    )

    assert result.outcome is ScreenshotResourceOutcome.SKIPPED


def test_per_viewport_resources_breaks_out_entries() -> None:
    capture = ScreenshotCaptureResult(
        requested=2,
        captured=1,
        failed=1,
        metadata_path=None,
        entries=[
            {"viewport": "desktop", "status": "success"},
            {"viewport": "mobile", "status": "failed", "error": "timeout"},
        ],
        errors=[
            ScreenshotError(
                error_type="TimeoutError",
                message="timed out",
                retryable=True,
            )
        ],
    )

    result = from_capture_result(
        capture,
        resource_key="screenshots",
        config={"viewports": ["desktop", "mobile"]},
    )

    viewports = per_viewport_resources(result)
    names = {v.viewport: v for v in viewports}
    assert set(names.keys()) == {"desktop", "mobile"}
    assert names["desktop"].outcome is ScreenshotResourceOutcome.SUCCESS
    assert names["mobile"].outcome is ScreenshotResourceOutcome.FAILED
    assert names["mobile"].metadata["failed"] == 1
