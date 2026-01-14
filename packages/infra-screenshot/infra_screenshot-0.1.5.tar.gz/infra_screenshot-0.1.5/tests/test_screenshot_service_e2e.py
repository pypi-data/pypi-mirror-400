from __future__ import annotations

import json
import os
import threading
import time
from collections.abc import Generator
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pytest

from screenshot import (
    ScreenshotBackend,
    ScreenshotBatchResult,
    ScreenshotCaptureResult,
    ScreenshotJob,
    ScreenshotOptions,
    ScreenshotService,
)
from screenshot.models import CaptureOptions
from screenshot.playwright_runner import capture_screenshots_async as playwright_capture_async

SITES_UNDER_TEST = [
    "https://landonorris.com/",
    "https://wonjyou.studio/",
    "https://algon.iq/",
]

SYSTEM_CHROME_PATH = "/usr/bin/google-chrome-stable"

_LOCAL_SITE_PAGES = {
    "/": (
        "<html><head><title>Local Home</title></head>"
        "<body><h1>It works!</h1><p id='content'>Local content</p></body></html>"
    ),
    "/gallery": (
        "<html><body><section><h2>Gallery</h2><img src='one.png'/>"
        "<img src='two.png'/></section></body></html>"
    ),
    "/slow": "<html><body><p>Slow page</p></body></html>",
}


def _require_e2e() -> None:
    if os.getenv("RUN_E2E") != "1":
        pytest.skip("Set RUN_E2E=1 to enable screenshot service E2E tests")


def _require_playwright() -> None:
    try:
        import playwright  # noqa: F401
    except ImportError as exc:  # pragma: no cover - optional dependency
        pytest.skip(f"Playwright is not installed ({exc}); skipping screenshot E2E test")


def _require_real_sites() -> None:
    if os.getenv("RUN_REAL_SITES") != "1":
        pytest.skip("Set RUN_REAL_SITES=1 to enable external site captures")


@pytest.fixture(autouse=True)
def _use_system_chrome(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PLAYWRIGHT_EXECUTABLE_PATH", SYSTEM_CHROME_PATH)


def _job_id_from_url(url: str) -> str:
    parsed = urlparse(url)
    parts = [parsed.netloc.replace(".", "-").strip("-")]
    if parsed.path and parsed.path not in {"/", ""}:
        segments = [segment for segment in parsed.path.split("/") if segment]
        parts.extend(segments[:2])
    job_id = "-".join(filter(None, parts)) or "site"
    return job_id.lower()


class _PlaywrightBackend(ScreenshotBackend[ScreenshotCaptureResult]):
    """Lightweight backend that forwards jobs to the Playwright runner."""

    async def run_job_async(self, job: ScreenshotJob) -> ScreenshotCaptureResult:
        result = await playwright_capture_async(
            job.job_id,
            job.url,
            store_dir=job.output_root,
            partition_date=job.partition_date,
            options=job.options,
            html_snapshot_path=job.html_snapshot_path,
            cancel_token=job.cancel_token,
        )
        if result.job_id is None:
            result.job_id = job.job_id
        return result


def _make_capture_options(**overrides: Any) -> CaptureOptions:
    """Create CaptureOptions with defaults and overrides.

    Args:
        **overrides: Keyword arguments matching CaptureOptions fields

    Returns:
        CaptureOptions instance with merged settings
    """
    defaults: dict[str, Any] = {
        "enabled": True,
        "max_pages": 1,
        "depth": 0,
        "viewports": ("desktop",),
        "post_nav_wait_s": 0.2,
        "timeout_s": 15.0,
        "max_capture_attempts": 1,
    }
    # Merge overrides with defaults
    defaults.update(overrides)

    # Create CaptureOptions, letting it validate the types
    return CaptureOptions(**defaults)


def _make_screenshot_options(**capture_overrides: Any) -> ScreenshotOptions:
    """Create ScreenshotOptions with default capture settings.

    Args:
        **capture_overrides: Keyword arguments for CaptureOptions

    Returns:
        ScreenshotOptions instance configured for testing
    """
    options = ScreenshotOptions(capture=_make_capture_options(**capture_overrides))
    options.runner.playwright_executable_path = SYSTEM_CHROME_PATH
    return options


def _assert_successful_capture(result: ScreenshotCaptureResult) -> None:
    assert result.succeeded, f"Screenshot capture failed for {result.job_id}: {result.errors}"
    assert result.captured >= 1, f"No screenshots captured for {result.job_id}"
    assert result.metadata_path is not None, f"Missing metadata path for {result.job_id}"
    metadata_path = result.metadata_path
    assert metadata_path.exists(), f"Metadata file missing at {metadata_path}"

    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    entries = payload.get("entries") if isinstance(payload, dict) else None
    assert entries, f"No metadata entries recorded for {result.job_id}"

    site_root = metadata_path.parent.parent
    screenshot_paths = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        rel_path = entry.get("screenshot_path")
        status = entry.get("status")
        if rel_path and status in {"captured", "success"}:
            candidate = Path(rel_path)
            if not candidate.is_absolute():
                candidate = site_root / rel_path
            screenshot_paths.append(candidate)

    assert screenshot_paths, f"No captured screenshot paths found for {result.job_id}"
    for screenshot_path in screenshot_paths:
        assert screenshot_path.exists(), f"Screenshot file missing at {screenshot_path}"


class _LocalSiteHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler signature
        if self.path == "/slow":
            time.sleep(1.5)
        body = _LOCAL_SITE_PAGES.get(self.path)
        if body is None:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return  # Silence per-test HTTP logging noise


@pytest.fixture(scope="module")
def local_test_site() -> Generator[str, None, None]:
    server = HTTPServer(("127.0.0.1", 0), _LocalSiteHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        yield base_url
    finally:
        server.shutdown()
        thread.join()


@pytest.mark.asyncio
async def test_screenshot_service_captures_local_site(tmp_path: Path, local_test_site: str) -> None:
    _require_e2e()
    _require_playwright()

    backend = _PlaywrightBackend()
    service = ScreenshotService(backend, concurrency=1)

    job = ScreenshotJob(
        job_id="local-home",
        url=f"{local_test_site}/",
        output_root=tmp_path,
        options=_make_screenshot_options(),
    )

    batch_result = await service.capture_async([job])
    assert len(batch_result.results) == 1
    _assert_successful_capture(batch_result.results[0])


@pytest.mark.asyncio
async def test_screenshot_service_captures_multiple_jobs(
    tmp_path: Path, local_test_site: str
) -> None:
    _require_e2e()
    _require_playwright()

    backend = _PlaywrightBackend()
    service = ScreenshotService(backend, concurrency=2)

    jobs = [
        ScreenshotJob(
            job_id="local-home",
            url=f"{local_test_site}/",
            output_root=tmp_path,
            options=_make_screenshot_options(),
        ),
        ScreenshotJob(
            job_id="local-gallery",
            url=f"{local_test_site}/gallery",
            output_root=tmp_path,
            options=_make_screenshot_options(post_nav_wait_s=0.3),
        ),
    ]

    batch_result = await service.capture_async(jobs)
    assert len(batch_result.results) == 2
    job_ids = {result.job_id for result in batch_result.results}
    assert job_ids == {"local-home", "local-gallery"}
    for result in batch_result.results:
        _assert_successful_capture(result)


@pytest.mark.asyncio
async def test_screenshot_service_scroll_tuning(tmp_path: Path, local_test_site: str) -> None:
    _require_e2e()
    _require_playwright()

    backend = _PlaywrightBackend()
    service = ScreenshotService(backend, concurrency=1)

    job = ScreenshotJob(
        job_id="local-scroll-tuning",
        url=f"{local_test_site}/",
        output_root=tmp_path,
        options=_make_screenshot_options(
            scroll=True,
            scroll_step_delay_ms=0,
            max_scroll_steps=1,
            pre_capture_wait_s=0.0,
        ),
    )

    batch_result = await service.capture_async([job])
    assert len(batch_result.results) == 1
    _assert_successful_capture(batch_result.results[0])


@pytest.mark.asyncio
async def test_screenshot_service_reports_failures(tmp_path: Path, local_test_site: str) -> None:
    _require_e2e()
    _require_playwright()

    backend = _PlaywrightBackend()
    service = ScreenshotService(backend, concurrency=2)

    good_job = ScreenshotJob(
        job_id="local-home",
        url=f"{local_test_site}/",
        output_root=tmp_path,
        options=_make_screenshot_options(),
    )
    failing_job = ScreenshotJob(
        job_id="bad-host",
        url="http://127.0.0.1:9/nope",
        output_root=tmp_path,
        options=_make_screenshot_options(timeout_s=5.0, max_capture_attempts=1),
    )

    batch_result = await service.capture_async([good_job, failing_job])
    assert len(batch_result.results) == 2
    successes = [result for result in batch_result.results if result.job_id == "local-home"]
    failures = [result for result in batch_result.results if result.job_id == "bad-host"]
    assert len(successes) == 1
    assert len(failures) == 1
    _assert_successful_capture(successes[0])
    failure = failures[0]
    assert not failure.succeeded
    assert failure.metadata_path and failure.metadata_path.exists()
    entry_errors = [
        entry.get("error")
        for entry in failure.entries
        if isinstance(entry, dict) and entry.get("error")
    ]
    assert failure.errors or entry_errors, "Expected failure to record error details"


@pytest.mark.asyncio
async def test_screenshot_service_captures_real_sites(tmp_path: Path) -> None:
    """End-to-end validation that the screenshot service captures real sites."""

    _require_e2e()
    _require_playwright()
    _require_real_sites()

    backend = _PlaywrightBackend()
    service = ScreenshotService(backend, concurrency=1)

    jobs: list[ScreenshotJob] = []
    for url in SITES_UNDER_TEST:
        job_id = _job_id_from_url(url)
        options = _make_screenshot_options(
            enabled=True,
            max_pages=1,
            depth=0,
            viewports=("desktop",),
            post_nav_wait_s=2.0,
            timeout_s=90.0,
            max_capture_attempts=2,
        )
        jobs.append(
            ScreenshotJob(
                job_id=job_id,
                url=url,
                output_root=tmp_path,
                options=options,
            )
        )

    batch_result: ScreenshotBatchResult = await service.capture_async(jobs)
    assert len(batch_result.results) == len(jobs)

    for result in batch_result.results:
        _assert_successful_capture(result)
