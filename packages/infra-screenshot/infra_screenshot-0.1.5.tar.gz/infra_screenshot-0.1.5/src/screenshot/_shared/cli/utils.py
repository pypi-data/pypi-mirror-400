"""Miscellaneous helpers for CLI processing."""

from __future__ import annotations

import re
from urllib.parse import urlparse

_SAFE_JOB_ID_RE = re.compile(r"[^a-z0-9-]+")


def derive_job_id(url: str, *, fallback: str = "job") -> str:
    """Consistently derive a job identifier from a URL."""

    if url:
        parsed = urlparse(url)
        parts = [parsed.netloc.replace(".", "-").strip("-")]
        if parsed.path and parsed.path not in {"/", ""}:
            segments = [segment for segment in parsed.path.split("/") if segment]
            parts.extend(segments[:2])
        job_id = "-".join(filter(None, parts)).lower()
        job_id = _SAFE_JOB_ID_RE.sub("-", job_id).strip("-")
        if job_id:
            return job_id
    return fallback


__all__ = ["derive_job_id"]
