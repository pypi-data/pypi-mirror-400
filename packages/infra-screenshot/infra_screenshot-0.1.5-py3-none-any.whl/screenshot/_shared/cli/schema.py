"""Dataclasses describing CLI inputs and intermediate records."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

__all__ = ["ScreenshotCliArgs", "RawJobRecord"]


@dataclass(frozen=True)
class ScreenshotCliArgs:
    """Lightweight view of CLI arguments consumed by job collection."""

    input: Path | None
    urls: Sequence[str]
    site_ids: Sequence[str]
    partition_date: str | None
    max_pages: int
    depth: int
    viewports: Sequence[str]
    post_nav_wait_s: float
    timeout_s: float
    max_retries: int | None
    job_budget_s: float | None
    scroll: bool | None = None
    scroll_step_delay_ms: int | None = None
    max_scroll_steps: int | None = None
    allow_autoplay: bool | None = None
    hide_overlays: bool | None = None
    reduced_motion: bool | None = None
    full_page: bool | None = None
    pre_capture_wait_s: float | None = None
    mute_media: bool | None = None
    disable_animations: bool | None = None
    block_media: bool | None = None
    extra_css_paths: Sequence[Path] = ()
    extra_js_paths: Sequence[Path] = ()
    chromium_compat: str | None = None
    max_viewport_concurrency: int | None = None
    override_custom_user_agent: str | None = None
    playwright_executable_path: str | None = None
    backend: str = "playwright"


@dataclass(frozen=True)
class RawJobRecord:
    """Raw job description before options are materialised."""

    job_id: str
    url: str
    backend: str
    partition_date: str | None
    html_snapshot_path: str | None
    metadata: dict[str, object]
    options_override: dict[str, object] | None
