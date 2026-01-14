"""TypedDict helpers that document shared payloads across CLI and services."""

from __future__ import annotations

from typing import TypedDict


class ScreenshotMetadata(TypedDict, total=False):
    """Metadata fields attached to CLI job specs or resource outcomes."""

    source: str
    backend: str
    job_id: str
    schema_version: str


class ScreenshotJobSpec(TypedDict):
    """Normalized CLI job spec forwarded to storage or APIs."""

    job_id: str
    url: str
    partition_date: str | None
    html_snapshot_path: str | None
    metadata: ScreenshotMetadata
    options: dict[str, object]
    backend: str
