from __future__ import annotations

import threading
from collections.abc import Generator
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import pytest

from screenshot.models import CaptureOptions, ScreenshotOptions
from screenshot.playwright_runner import capture_screenshots_async


class _SmokeHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - signature defined by BaseHTTPRequestHandler
        body = (
            "<html><head><title>Smoke</title></head>"
            "<body><h1>Smoke Test</h1><p id='content'>ok</p></body></html>"
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return  # keep pytest output clean


@pytest.fixture(scope="module")
def smoke_site() -> Generator[str, None, None]:
    try:
        server = HTTPServer(("127.0.0.1", 0), _SmokeHandler)
    except PermissionError:
        pytest.skip(
            "Cannot bind HTTP server inside this environment; smoke test needs network access"
        )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        yield base
    finally:
        server.shutdown()
        thread.join()


def _smoke_options(**capture_overrides: Any) -> ScreenshotOptions:
    capture = CaptureOptions(
        enabled=True,
        max_pages=1,
        depth=0,
        viewports=("desktop",),
        post_nav_wait_s=0.1,
        timeout_s=20.0,
        max_capture_attempts=1,
    )
    if capture_overrides:
        capture = replace(capture, **capture_overrides)
    return ScreenshotOptions(capture=capture)


@pytest.mark.asyncio
async def test_capture_local_site_smoke(tmp_path: Path, smoke_site: str) -> None:
    pytest.importorskip("playwright.async_api")

    result = await capture_screenshots_async(
        "smoke",
        f"{smoke_site}/",
        store_dir=tmp_path,
        partition_date=None,
        options=_smoke_options(),
    )

    if result.errors and any("playwright" in err.message.lower() for err in result.errors):
        pytest.skip(
            "Playwright capture failed; run `playwright install chromium` "
            "(and ensure the browsers are available) before rerunning the smoke test."
        )

    assert result.succeeded
    assert result.metadata_path and result.metadata_path.exists()
    entries = result.entries
    assert entries, "Expected metadata entries for smoke job"


@pytest.mark.asyncio
async def test_capture_failure_records_errors(tmp_path: Path) -> None:
    pytest.importorskip("playwright.async_api")

    bad_url = "http://127.0.0.1:9/does-not-exist"
    result = await capture_screenshots_async(
        "smoke-failure",
        bad_url,
        store_dir=tmp_path,
        partition_date=None,
        options=_smoke_options(timeout_s=5.0),
    )

    assert not result.succeeded
    assert result.errors or any(
        isinstance(entry, dict) and entry.get("error") for entry in result.entries
    )
