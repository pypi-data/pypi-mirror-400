from __future__ import annotations

from test_utils import create_capture_result

from screenshot import ScreenshotCaptureResult
from screenshot._internal import from_capture_result, per_viewport_resources
from screenshot._shared.errors import ScreenshotError


def test_from_capture_result_builds_resource() -> None:
    capture = create_capture_result(requested=1, captured=1, failed=0)
    result = from_capture_result(
        capture,
        resource_key="key",
        config={"viewports": ["desktop"], "depth": 1, "timeout_s": 30},
    )

    assert result.outcome.name == "SUCCESS"
    assert result.metadata["requested"] == 1


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
        errors=[ScreenshotError(error_type="TimeoutError", message="timeout", retryable=True)],
    )
    resource = from_capture_result(
        capture,
        resource_key="key",
        config={"viewports": ["desktop", "mobile"]},
    )
    viewports = per_viewport_resources(resource)
    assert {v.viewport for v in viewports} == {"desktop", "mobile"}
