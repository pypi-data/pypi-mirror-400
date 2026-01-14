"""Transformations moved out of the public dataclasses for easier testing."""

from __future__ import annotations

import json
from hashlib import sha256

from .._models_results import (
    ScreenshotCaptureResult,
    ScreenshotResourceError,
    ScreenshotResourceOutcome,
    ScreenshotResourceResult,
    ScreenshotViewportResource,
)
from .._shared.errors import ErrorCategory, ScreenshotError


def _entry_succeeded(entry: dict[str, object]) -> bool:
    return str(entry.get("status") or "").lower() == "success" and not entry.get("error")


def _entry_failed(entry: dict[str, object]) -> bool:
    return not _entry_succeeded(entry)


def _determine_viewport_outcome(
    *,
    global_outcome: ScreenshotResourceOutcome,
    requested: int,
    captured: int,
    failed: int,
) -> ScreenshotResourceOutcome:
    if requested == 0:
        return global_outcome
    if failed == 0:
        return ScreenshotResourceOutcome.SUCCESS
    if captured == 0:
        return ScreenshotResourceOutcome.FAILED
    return ScreenshotResourceOutcome.PARTIAL


def _categorize_screenshot_error(err: ScreenshotError) -> str:
    return ErrorCategory.from_error_type(err.error_type).value


def generate_screenshot_config_key(config: dict[str, object]) -> str:
    viewports_val = config.get("viewports", [])
    if isinstance(viewports_val, list | tuple):
        viewports_list = [str(v) for v in viewports_val]
    else:
        viewports_list = [str(viewports_val)] if viewports_val is not None else []
    normalized = {
        "viewports": sorted(viewports_list),
        "depth": config.get("depth", 0),
        "timeout_s": config.get("timeout_s", 60.0),
        "scroll": bool(config.get("scroll", False)),
        "full_page": bool(config.get("full_page", False)),
    }
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def from_capture_result(
    capture_result: ScreenshotCaptureResult,
    *,
    resource_key: str,
    config: dict[str, object],
    metadata: dict[str, object] | None = None,
) -> ScreenshotResourceResult:
    if capture_result.requested == 0:
        outcome = ScreenshotResourceOutcome.SKIPPED
    elif capture_result.captured == 0 and capture_result.requested > 0:
        outcome = ScreenshotResourceOutcome.FAILED
    elif capture_result.failed > 0:
        outcome = ScreenshotResourceOutcome.PARTIAL
    else:
        outcome = ScreenshotResourceOutcome.SUCCESS

    resource_errors = [
        ScreenshotResourceError(
            category=_categorize_screenshot_error(err),
            message=err.message,
            retryable=err.retryable,
            details=dict(err.details),
        )
        for err in capture_result.errors
    ]

    default_metadata = {
        "requested": capture_result.requested,
        "captured": capture_result.captured,
        "failed": capture_result.failed,
        "job_id": capture_result.job_id,
        "metadata_path": str(capture_result.metadata_path)
        if capture_result.metadata_path
        else None,
        "entries": list(capture_result.entries),
    }

    return ScreenshotResourceResult(
        resource_key=resource_key,
        outcome=outcome,
        config_key=generate_screenshot_config_key(config),
        errors=resource_errors,
        metadata={**default_metadata, **(metadata or {})},
        entries=list(capture_result.entries),
    )


def per_viewport_resources(
    resource_result: ScreenshotResourceResult,
) -> list[ScreenshotViewportResource]:
    if not resource_result.entries:
        return [
            ScreenshotViewportResource(
                resource_key=resource_result.resource_key,
                viewport="default",
                outcome=resource_result.outcome,
                config_key=resource_result.config_key,
                errors=list(resource_result.errors),
                metadata=dict(resource_result.metadata),
            )
        ]

    by_viewport: dict[str, list[dict[str, object]]] = {}
    for entry in resource_result.entries:
        viewport = str(entry.get("viewport") or "default").lower()
        by_viewport.setdefault(viewport, []).append(entry)

    results: list[ScreenshotViewportResource] = []
    for viewport, entries in by_viewport.items():
        requested = len(entries)
        captured = sum(1 for e in entries if _entry_succeeded(e))
        failed = sum(1 for e in entries if _entry_failed(e))
        metadata = dict(resource_result.metadata)
        metadata.update(
            {
                "viewport": viewport,
                "entries": entries,
                "requested": requested,
                "captured": captured,
                "failed": failed,
            }
        )
        viewport_outcome = _determine_viewport_outcome(
            global_outcome=resource_result.outcome,
            requested=requested,
            captured=captured,
            failed=failed,
        )
        results.append(
            ScreenshotViewportResource(
                resource_key=resource_result.resource_key,
                viewport=viewport,
                outcome=viewport_outcome,
                config_key=resource_result.config_key,
                errors=list(resource_result.errors),
                metadata=metadata,
            )
        )
    return results
