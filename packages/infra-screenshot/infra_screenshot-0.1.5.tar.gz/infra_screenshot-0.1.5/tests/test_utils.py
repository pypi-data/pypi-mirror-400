"""Shared test utilities for screenshot tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from screenshot import ScreenshotCaptureResult
from screenshot._shared.errors import ScreenshotError


def create_capture_result(
    *,
    requested: int,
    captured: int,
    failed: int,
    errors: list[ScreenshotError] | None = None,
    metadata_path: Path | None = None,
    entries: list[dict[str, Any]] | None = None,
    job_id: str = "job-123",
) -> ScreenshotCaptureResult:
    """Create a ScreenshotCaptureResult for testing.

    Args:
        requested: Number of screenshots requested.
        captured: Number of screenshots captured.
        failed: Number of screenshots failed.
        errors: Optional list of errors.
        metadata_path: Path to metadata file (defaults to /tmp/meta.json).
        entries: Metadata entries (defaults to single desktop viewport).
        job_id: Job identifier (defaults to "job-123").

    Returns:
        ScreenshotCaptureResult instance for testing.
    """
    return ScreenshotCaptureResult(
        requested=requested,
        captured=captured,
        failed=failed,
        metadata_path=metadata_path or Path("/tmp/meta.json"),
        entries=entries or [{"viewport": "desktop"}],
        errors=list(errors or []),
        job_id=job_id,
    )
