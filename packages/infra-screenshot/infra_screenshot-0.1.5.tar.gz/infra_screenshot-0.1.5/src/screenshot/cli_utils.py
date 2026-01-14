"""Shared helpers for screenshot CLI commands."""

from __future__ import annotations

from typing import NotRequired, TypedDict

from ._shared.cli.options import build_options
from ._shared.cli.parser import load_cli_inputs
from ._shared.cli.schema import ScreenshotCliArgs
from ._shared.cli.utils import derive_job_id
from ._shared.cli.validator import validate_backend_choice
from ._shared.options_normalizer import ensure_sequence_lists
from .models import ScreenshotOptions


class ScreenshotSpecMetadata(TypedDict, total=False):
    """Normalized metadata attached to each CLI job spec."""

    source: NotRequired[str]
    backend: NotRequired[str]
    schema_version: NotRequired[str]
    campaign: NotRequired[str]


class ScreenshotJobSpec(TypedDict):
    """Explicit schema for the job spec returned by `collect_job_specs`."""

    job_id: str
    url: str
    partition_date: str | None
    html_snapshot_path: str | None
    metadata: ScreenshotSpecMetadata
    options: ScreenshotOptions
    backend: str


def collect_job_specs(args: ScreenshotCliArgs) -> list[ScreenshotJobSpec]:
    """Return normalized screenshot job specs from CLI arguments."""

    backend = (args.backend or "playwright").strip().lower()
    records, css_snippets, js_snippets = load_cli_inputs(args)

    specs: list[ScreenshotJobSpec] = []
    for record in records:
        options = build_options(
            args=args,
            css_snippets=css_snippets,
            js_snippets=js_snippets,
            overrides=record.options_override,
        )
        validate_backend_choice(backend, options)

        metadata: ScreenshotSpecMetadata = dict(record.metadata)  # type: ignore[assignment]
        metadata.setdefault("backend", backend)

        specs.append(
            {
                "job_id": record.job_id,
                "url": record.url,
                "partition_date": record.partition_date,
                "html_snapshot_path": record.html_snapshot_path,
                "metadata": metadata,
                "options": options,
                "backend": backend,
            }
        )

    return specs


def spec_to_api_payload(spec: ScreenshotJobSpec) -> dict[str, object]:
    """Convert a job spec into the payload expected by the screenshot service."""

    payload: dict[str, object] = {
        "job_id": spec["job_id"],
        "url": spec["url"],
        "partition_date": spec["partition_date"],
        "metadata": dict(spec["metadata"]),
        "options": serialize_options(spec["options"]),
    }
    backend_value = spec.get("backend")
    if backend_value:
        payload["backend"] = backend_value
    snapshot = spec.get("html_snapshot_path")
    if snapshot:
        payload["html_snapshot_path"] = snapshot
    return payload


def serialize_options(options: ScreenshotOptions) -> dict[str, object]:
    """Serialize ScreenshotOptions to simple types for JSON payloads."""

    normalized = ensure_sequence_lists(options)
    payload = normalized.to_dict()
    return payload


__all__ = [
    "collect_job_specs",
    "spec_to_api_payload",
    "serialize_options",
    "derive_job_id",
    "ScreenshotCliArgs",
]
