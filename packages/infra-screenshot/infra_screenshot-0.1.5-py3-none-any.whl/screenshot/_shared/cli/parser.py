"""Parsing helpers that fan out CLI arguments into raw job records."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from .schema import RawJobRecord, ScreenshotCliArgs
from .utils import derive_job_id

__all__ = ["load_cli_inputs"]


def _load_snippets(paths: Sequence[Path]) -> list[str]:
    snippets: list[str] = []
    for path in paths:
        snippets.append(path.read_text(encoding="utf-8"))
    return snippets


def load_cli_inputs(args: ScreenshotCliArgs) -> tuple[list[RawJobRecord], list[str], list[str]]:
    """Return raw job records plus pre-loaded CSS/JS snippets."""

    backend = (args.backend or "playwright").strip().lower()
    css_snippets = _load_snippets(args.extra_css_paths)
    js_snippets = _load_snippets(args.extra_js_paths)

    records: list[RawJobRecord] = []

    if args.input:
        with args.input.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                url = (record.get("url") or "").strip()
                if not url:
                    continue
                job_id = (
                    record.get("job_id") or record.get("site_id") or ""
                ).strip() or derive_job_id(url)
                partition = record.get("partition_date") or args.partition_date
                overrides = (
                    record.get("options") if isinstance(record.get("options"), dict) else None
                )
                snapshot = record.get("html_snapshot_path")
                snapshot_path = str(snapshot).strip() if snapshot else None
                metadata = record.get("metadata")
                metadata_dict = dict(metadata) if isinstance(metadata, dict) else {}
                metadata_dict.setdefault("source", "cli")
                records.append(
                    RawJobRecord(
                        job_id=job_id,
                        url=url,
                        backend=backend,
                        partition_date=partition,
                        html_snapshot_path=snapshot_path,
                        metadata=metadata_dict,
                        options_override=overrides,
                    )
                )

    urls = [url.strip() for url in (args.urls or []) if url and url.strip()]
    site_ids = [sid.strip() for sid in (args.site_ids or []) if sid and sid.strip()]
    if urls:
        for index, url in enumerate(urls):
            fallback = f"site-{index + 1}"
            job_id = (
                site_ids[index] if index < len(site_ids) else derive_job_id(url, fallback=fallback)
            )
            records.append(
                RawJobRecord(
                    job_id=job_id,
                    url=url,
                    backend=backend,
                    partition_date=args.partition_date,
                    html_snapshot_path=None,
                    metadata={"source": "cli", "input": "args"},
                    options_override=None,
                )
            )

    return records, css_snippets, js_snippets
