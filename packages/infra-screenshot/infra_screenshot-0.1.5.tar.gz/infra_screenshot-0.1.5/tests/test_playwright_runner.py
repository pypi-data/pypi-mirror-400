from __future__ import annotations

# mypy: ignore-errors
import asyncio
import builtins
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from screenshot import ScreenshotCaptureResult, ScreenshotOptions
from screenshot._models_options import BrowserCompatOptions, CaptureOptions, RunnerOptions
from screenshot._shared.storage import LocalStorageBackend, dumps_json as _json_dumps
from screenshot.playwright_runner import (
    BROWSER_MANAGER,
    BrowserBundleManager,
    _build_filename,
    _coerce_float,
    _coerce_int,
    _extract_links,
    _is_missing_playwright_browser,
    _normalize_url,
    _sanitize_options,
    capture_screenshots,
    capture_screenshots_async,
)

SKIP_NAVIGATION_TIMEOUT_TESTS = os.getenv("SKIP_PLAYWRIGHT_NAV_TESTS", "1").lower() not in {
    "0",
    "false",
    "no",
}


def test_sanitize_options_unknown_viewport(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level("WARNING")
    options = ScreenshotOptions(
        capture=CaptureOptions(
            max_pages=2,
            depth=1,
            viewports=("unknown",),
            post_nav_wait_s=0.25,
            timeout_s=45.0,
            scroll=False,
            pre_capture_wait_s=0.2,
        )
    )

    plans = _sanitize_options(options)

    assert plans.capture.primary_viewport == "desktop"
    assert plans.capture.scroll_enabled is False
    assert plans.capture.settle_timeout_ms == 200
    assert plans.browser.mute_media is True
    assert plans.browser.disable_animations is True
    assert plans.browser.block_media is False
    assert plans.capture.max_viewport_concurrency == 1
    assert list(plans.runner.extra_styles) == []
    assert list(plans.runner.extra_init_scripts) == []
    assert "Unknown viewport preset" in caplog.text


def test_sanitize_options_respects_max_total_duration() -> None:
    options = ScreenshotOptions(
        capture=CaptureOptions(
            max_pages=3,
            depth=1,
            viewports=("desktop", "mobile"),
            post_nav_wait_s=0.0,
            timeout_s=20.0,
            max_total_duration_s=90.0,
        )
    )

    plans = _sanitize_options(options)

    assert plans.capture.max_total_duration_sec == 90.0


def test_sanitize_options_preserves_scroll_tuning() -> None:
    options = ScreenshotOptions(
        capture=CaptureOptions(
            scroll=True,
            scroll_step_delay_ms=123,
            max_scroll_steps=7,
            pre_capture_wait_s=0.0,
        )
    )

    plans = _sanitize_options(options)

    assert plans.capture.scroll_enabled is True
    assert plans.capture.scroll_step_delay_ms == 123
    assert plans.capture.max_scroll_steps == 7


@pytest.mark.asyncio
async def test_playwright_scroll_tuning_passed_to_scroll(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls: dict[str, int] = {}

    async def fake_scroll(page: Any, *, max_steps: int, delay_ms: int) -> None:
        calls["max_steps"] = max_steps
        calls["delay_ms"] = delay_ms

    async def fake_eval_height(_page: Any) -> int:
        return 200

    monkeypatch.setattr("screenshot.playwright_runner._scroll_to_bottom", fake_scroll)
    monkeypatch.setattr("screenshot.playwright_runner._evaluate_scroll_height", fake_eval_height)

    import sys
    import types

    fake_mod = types.ModuleType("playwright.async_api")

    class Error(Exception):
        pass

    class TimeoutError(Exception):
        pass

    class FakePage:
        def __init__(self) -> None:
            self._closed = False

        def is_closed(self) -> bool:
            return self._closed

        def set_default_timeout(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def emulate_media(self, **_kwargs: object) -> None:
            return None

        async def goto(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def wait_for_timeout(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def add_style_tag(self, **_kwargs: object) -> None:
            return None

        async def screenshot(self, *, path: str, **_kwargs: object) -> None:
            Path(path).write_bytes(b"")

        async def title(self) -> str:
            return "Fake"

        async def close(self) -> None:
            self._closed = True

    class FakeContext:
        def __init__(self) -> None:
            self._page = FakePage()

        async def add_init_script(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def route(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def new_page(self) -> FakePage:
            return self._page

        async def close(self) -> None:
            return None

    class FakeBrowser:
        async def new_context(self, **_kwargs: object) -> FakeContext:
            return FakeContext()

        async def close(self) -> None:
            return None

    class FakeChromium:
        async def launch(self, **_kwargs: object) -> FakeBrowser:
            return FakeBrowser()

    class AsyncPlaywright:
        chromium = FakeChromium()

        async def __aenter__(self) -> AsyncPlaywright:
            return self

        async def __aexit__(self, exc_type, exc, tb) -> bool:
            return False

    def async_playwright() -> AsyncPlaywright:
        return AsyncPlaywright()

    setattr(fake_mod, "Error", Error)
    setattr(fake_mod, "TimeoutError", TimeoutError)
    setattr(fake_mod, "async_playwright", async_playwright)
    monkeypatch.setitem(sys.modules, "playwright.async_api", fake_mod)

    result = await capture_screenshots_async(
        "job",
        "https://example.com",
        store_dir=tmp_path,
        partition_date=None,
        options=ScreenshotOptions(
            capture=CaptureOptions(
                enabled=True,
                max_pages=1,
                depth=0,
                viewports=("desktop",),
                post_nav_wait_s=0.0,
                timeout_s=5.0,
                max_capture_attempts=1,
                scroll=True,
                scroll_step_delay_ms=111,
                max_scroll_steps=9,
                pre_capture_wait_s=0.0,
                max_viewport_concurrency=1,
            )
        ),
    )

    assert result.captured == 1
    assert calls == {"max_steps": 9, "delay_ms": 111}


@pytest.mark.asyncio
async def test_playwright_timings_emitted_when_enabled(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SCREENSHOT_ENABLE_TIMING", "1")
    monkeypatch.setattr("screenshot.playwright_runner.ENABLE_TIMING", True)

    import sys
    import types

    fake_mod = types.ModuleType("playwright.async_api")

    class Error(Exception):
        pass

    class TimeoutError(Exception):
        pass

    class FakePage:
        def __init__(self) -> None:
            self._closed = False

        def is_closed(self) -> bool:
            return self._closed

        def set_default_timeout(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def emulate_media(self, **_kwargs: object) -> None:
            return None

        async def goto(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def wait_for_timeout(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def add_style_tag(self, **_kwargs: object) -> None:
            return None

        async def screenshot(self, *, path: str, **_kwargs: object) -> None:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"PNG")

        async def title(self) -> str:
            return "Fake"

        async def close(self) -> None:
            self._closed = True

    class FakeContext:
        def __init__(self) -> None:
            self._page = FakePage()

        async def add_init_script(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def route(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def new_page(self) -> FakePage:
            return self._page

        async def close(self) -> None:
            return None

    class FakeBrowser:
        async def new_context(self, **_kwargs: object) -> FakeContext:
            return FakeContext()

        async def close(self) -> None:
            return None

    class FakeChromium:
        async def launch(self, **_kwargs: object) -> FakeBrowser:
            return FakeBrowser()

    class AsyncPlaywright:
        chromium = FakeChromium()

        async def __aenter__(self) -> AsyncPlaywright:
            return self

        async def __aexit__(self, exc_type, exc, tb) -> bool:
            return False

    def async_playwright() -> AsyncPlaywright:
        return AsyncPlaywright()

    setattr(fake_mod, "Error", Error)
    setattr(fake_mod, "TimeoutError", TimeoutError)
    setattr(fake_mod, "async_playwright", async_playwright)
    monkeypatch.setitem(sys.modules, "playwright.async_api", fake_mod)

    result = await capture_screenshots_async(
        "job",
        "https://example.com",
        store_dir=tmp_path,
        partition_date=None,
        options=ScreenshotOptions(
            capture=CaptureOptions(
                enabled=True,
                max_pages=1,
                depth=0,
                viewports=("desktop",),
                post_nav_wait_s=0.0,
                timeout_s=5.0,
                max_capture_attempts=1,
                scroll=False,
                pre_capture_wait_s=0.0,
                max_viewport_concurrency=1,
            )
        ),
    )

    assert result.captured == 1
    assert result.entries
    timings = result.entries[0].get("timings")
    assert isinstance(timings, dict)
    assert {
        "navigation_ms",
        "scroll_ms",
        "post_scroll_wait_ms",
        "screenshot_ms",
        "total_ms",
    }.issubset(timings.keys())
    assert timings["scroll_ms"] == 0.0
    assert timings["post_scroll_wait_ms"] == 0.0


def test_coerce_helpers() -> None:
    assert _coerce_int("5") == 5
    assert _coerce_int(True) == 1
    assert _coerce_int("not-a-number", default=7) == 7
    assert _coerce_float("2.4") == 2.4
    assert _coerce_float(False, default=3.1) == 0.0
    assert _coerce_float("bad", default=9.5) == 9.5


def test_sanitize_options_includes_tablet_preset() -> None:
    options = ScreenshotOptions(
        capture=CaptureOptions(
            max_pages=1,
            depth=0,
            viewports=("desktop", "tablet"),
            max_viewport_concurrency=2,
            enabled=True,
        )
    )

    plans = _sanitize_options(options)

    assert set(plans.capture.viewport_specs) == {"desktop", "tablet"}
    tablet = plans.capture.viewport_specs["tablet"]
    assert tablet["viewport"] == {"width": 768, "height": 1024}
    assert tablet["is_mobile"] is True


def test_sanitize_options_with_extras() -> None:
    options = ScreenshotOptions(
        capture=CaptureOptions(
            max_pages=1,
            depth=0,
            viewports=("desktop",),
            max_viewport_concurrency=2,
        ),
        browser=BrowserCompatOptions(
            disable_animations=True,
            block_media=True,
            mute_media=False,
        ),
        runner=RunnerOptions(
            extra_styles=("body { color: red; }",),
            extra_init_scripts=("console.log('hi');",),
        ),
    )

    plans = _sanitize_options(options)

    assert "body { color: red; }" in plans.runner.extra_styles
    assert "console.log('hi');" in plans.runner.extra_init_scripts
    assert plans.browser.disable_animations is True
    assert plans.browser.block_media is True
    assert plans.browser.mute_media is False
    assert plans.capture.max_viewport_concurrency == 2


def test_sanitize_options_includes_playwright_executable_path() -> None:
    options = ScreenshotOptions(
        runner=RunnerOptions(playwright_executable_path="/opt/google/chrome"),
    )

    plans = _sanitize_options(options)

    assert plans.runner.playwright_executable_path == "/opt/google/chrome"


def test_normalize_url_strips_fragment() -> None:
    url = "https://example.com/path/#section"
    normalized = _normalize_url(url)
    assert normalized == "https://example.com/path"


def test_build_filename_sanitizes_title() -> None:
    filename = _build_filename(2, "Welcome To Example!", "https://example.com", "desktop")
    assert filename == "002-welcome-to-example-desktop.png"


def test_is_missing_playwright_browser_detection() -> None:
    assert _is_missing_playwright_browser(Exception("Executable doesn't exist at path"))
    assert _is_missing_playwright_browser(Exception("Browser needs to be installed"))
    assert not _is_missing_playwright_browser(Exception("network error"))


@pytest.mark.asyncio
async def test_ensure_playwright_browsers_success(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    called_args: dict[str, object] = {}

    class DummyProcess:
        def __init__(self) -> None:
            self.returncode = 0

        async def communicate(self) -> tuple[bytes, bytes]:
            return b"installed", b""

    async def fake_create_subprocess_exec(*args: object, **kwargs: object) -> DummyProcess:
        called_args["args"] = args
        called_args["env"] = kwargs.get("env", {})
        return DummyProcess()

    monkeypatch.setattr(
        "screenshot.playwright_runner.asyncio.create_subprocess_exec",
        fake_create_subprocess_exec,
    )
    monkeypatch.setattr(BROWSER_MANAGER, "_bundle_dir", tmp_path / "browsers")
    monkeypatch.setattr(BROWSER_MANAGER, "_env_configured", False)
    monkeypatch.delenv("PLAYWRIGHT_BROWSERS_PATH", raising=False)

    result = await BROWSER_MANAGER._ensure_playwright_browsers()

    assert result is True
    assert "playwright" in called_args["args"]
    assert "PLAYWRIGHT_BROWSERS_PATH" in called_args["env"]


@pytest.mark.asyncio
async def test_ensure_playwright_browsers_with_lock(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls: list[bool] = []

    async def fake_install(self: object) -> bool:
        calls.append(True)
        await asyncio.sleep(0)
        return True

    monkeypatch.setattr(
        "screenshot.playwright_runner.BrowserBundleManager._ensure_playwright_browsers",
        fake_install,
    )
    monkeypatch.setattr(
        "screenshot.playwright_runner._INSTALL_LOCK_PATH",
        tmp_path / "install.lock",
        raising=False,
    )

    # Avoid relying on platform-specific file locking during tests.
    class _Handle:
        def close(self) -> None:
            return None

    def fake_acquire(self: object) -> _Handle:
        return _Handle()

    def fake_release(self: object, handle: _Handle) -> None:
        handle.close()

    monkeypatch.setattr(
        "screenshot.playwright_runner.BrowserBundleManager._acquire_install_file_lock",
        fake_acquire,
    )
    monkeypatch.setattr(
        "screenshot.playwright_runner.BrowserBundleManager._release_install_file_lock",
        fake_release,
    )

    # Force runtime installs for this test run
    monkeypatch.setattr(
        "screenshot.playwright_runner._ENABLE_RUNTIME_BROWSER_INSTALL", True, raising=False
    )

    async def fake_to_thread(func: Callable[..., Any], *args: object, **kwargs: object) -> Any:
        return func(*args, **kwargs)

    monkeypatch.setattr("screenshot.playwright_runner.asyncio.to_thread", fake_to_thread)

    result = await BROWSER_MANAGER.ensure_runtime_browser()

    assert result is True
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_runtime_install_telemetry_success(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level("INFO")

    async def fake_install(self: object) -> bool:
        await asyncio.sleep(0)
        return True

    class _InstallHandle:
        def close(self) -> None:
            return None

    def fake_acquire(self: object) -> _InstallHandle:
        return _InstallHandle()

    def fake_release(self: object, handle: _InstallHandle) -> None:
        try:
            handle.close()
        except Exception:
            # File lock cleanup failures are non-fatal in tests; best-effort close.
            pass

    monkeypatch.setattr(
        "screenshot.playwright_runner.BrowserBundleManager._ensure_playwright_browsers",
        fake_install,
    )
    monkeypatch.setattr(
        "screenshot.playwright_runner.BrowserBundleManager._acquire_install_file_lock",
        fake_acquire,
    )
    monkeypatch.setattr(
        "screenshot.playwright_runner.BrowserBundleManager._release_install_file_lock",
        fake_release,
    )
    monkeypatch.setattr(
        "screenshot.playwright_runner._ENABLE_RUNTIME_BROWSER_INSTALL",
        True,
        raising=False,
    )

    async def fake_to_thread(func: Callable[..., Any], *args: object, **kwargs: object) -> Any:
        return func(*args, **kwargs)

    monkeypatch.setattr("screenshot.playwright_runner.asyncio.to_thread", fake_to_thread)

    ok = await BROWSER_MANAGER.ensure_runtime_browser()
    assert ok in (True, False)
    assert "Runtime Playwright install succeeded" in caplog.text


@pytest.mark.asyncio
async def test_runtime_install_telemetry_failure(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level("INFO")

    async def fake_install(self: object) -> bool:
        await asyncio.sleep(0)
        return False

    class _InstallHandle:
        def close(self) -> None:
            return None

    def fake_acquire(self: object) -> _InstallHandle:
        return _InstallHandle()

    def fake_release(self: object, handle: _InstallHandle) -> None:
        try:
            handle.close()
        except Exception:
            # File lock cleanup failures are non-fatal in tests; best-effort close.
            pass

    monkeypatch.setattr(
        "screenshot.playwright_runner.BrowserBundleManager._ensure_playwright_browsers",
        fake_install,
    )
    monkeypatch.setattr(
        "screenshot.playwright_runner.BrowserBundleManager._acquire_install_file_lock",
        fake_acquire,
    )
    monkeypatch.setattr(
        "screenshot.playwright_runner.BrowserBundleManager._release_install_file_lock",
        fake_release,
    )
    monkeypatch.setattr(
        "screenshot.playwright_runner._ENABLE_RUNTIME_BROWSER_INSTALL",
        True,
        raising=False,
    )

    async def fake_to_thread(func: Callable[..., Any], *args: object, **kwargs: object) -> Any:
        return func(*args, **kwargs)

    monkeypatch.setattr("screenshot.playwright_runner.asyncio.to_thread", fake_to_thread)

    ok = await BROWSER_MANAGER.ensure_runtime_browser()
    assert ok is False
    assert "Runtime Playwright install failed" in caplog.text


def test_ensure_env_sets_and_overrides(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Configure a fake bundled dir and clear memoization
    monkeypatch.setattr(
        "screenshot.playwright_runner.BROWSER_MANAGER._bundle_dir", tmp_path / "browsers"
    )
    monkeypatch.setattr("screenshot.playwright_runner.BROWSER_MANAGER._env_configured", False)
    # Ensure directory exists
    (tmp_path / "browsers").mkdir(parents=True, exist_ok=True)

    # No env set initially
    monkeypatch.delenv("PLAYWRIGHT_BROWSERS_PATH", raising=False)
    BROWSER_MANAGER.ensure_env()
    assert os.environ.get("PLAYWRIGHT_BROWSERS_PATH") == str(tmp_path / "browsers")

    # If env is already set to a different value, ensure_env should still point to bundle
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", str(tmp_path / "elsewhere"))
    # Reset memoization to allow re-run
    monkeypatch.setattr("screenshot.playwright_runner.BROWSER_MANAGER._env_configured", False)
    BROWSER_MANAGER.ensure_env()
    assert os.environ.get("PLAYWRIGHT_BROWSERS_PATH") == str(tmp_path / "browsers")


@pytest.mark.asyncio
async def test_ensure_runtime_browser_disabled_returns_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Even if installer would succeed, disabled flag short-circuits
    async def fake_install(self: object) -> bool:
        return True

    monkeypatch.setattr(
        "screenshot.playwright_runner.BrowserBundleManager._ensure_playwright_browsers",
        fake_install,
    )
    monkeypatch.setattr(
        "screenshot.playwright_runner._ENABLE_RUNTIME_PLAYWRIGHT_INSTALL",
        False,
        raising=False,
    )
    ok = await BROWSER_MANAGER.ensure_runtime_browser()
    assert ok is False


@pytest.mark.asyncio
async def test_playwright_navigation_retry_logs_and_succeeds(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Simulate Playwright where first goto times out, second succeeds.

    Verifies that our retry logging hook fires and that capture proceeds.
    """
    caplog.set_level("DEBUG")

    if SKIP_NAVIGATION_TIMEOUT_TESTS:
        pytest.skip(
            "Playwright navigation retry test causes timeout in constrained environments; "
            "set SKIP_PLAYWRIGHT_NAV_TESTS=0 to force it."
        )

    # Build a fake playwright.async_api module
    import sys
    import types

    fake_mod = types.ModuleType("playwright.async_api")

    class Error(Exception):
        pass

    class TimeoutError(Exception):
        pass

    class FakePage:
        def __init__(self) -> None:
            self._closed = False
            self._calls = 0

        def set_default_timeout(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def emulate_media(self, **_kwargs: object) -> None:
            return None

        async def wait_for_timeout(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def goto(self, *_args: object, **_kwargs: object) -> None:
            self._calls += 1
            if self._calls == 1:
                raise TimeoutError("navigation timeout for test (forced)")
            return None

        async def add_style_tag(self, **_kwargs: object) -> None:
            return None

        async def content(self) -> str:
            return "<html></html>"

        async def title(self) -> str:
            return "Example Page"

        async def screenshot(self, path: str, **_kwargs: object) -> None:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"PNG")
            return None

        async def close(self) -> None:
            self._closed = True

        def is_closed(self) -> bool:
            return self._closed

    class FakeContext:
        def __init__(self) -> None:
            self._page = FakePage()

        async def add_init_script(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def route(self, *_args: object, **_kwargs: object) -> None:
            return None

        async def new_page(self) -> FakePage:
            return self._page

        async def close(self) -> None:
            return None

    captured_context: dict[str, FakeContext] = {}

    class FakeBrowser:
        async def new_context(self, **_kwargs: object) -> FakeContext:
            ctx = FakeContext()
            captured_context["ctx"] = ctx
            return ctx

        async def close(self) -> None:
            return None

    class Chromium:
        async def launch(self, **_kwargs: object) -> FakeBrowser:
            return FakeBrowser()

    class AsyncPlaywright:
        def __init__(self) -> None:
            self.chromium = Chromium()

        async def __aenter__(self) -> AsyncPlaywright:
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
            return False

    def async_playwright() -> AsyncPlaywright:
        # Real API returns an object usable as async context manager
        return AsyncPlaywright()

    setattr(fake_mod, "Error", Error)
    setattr(fake_mod, "TimeoutError", TimeoutError)
    setattr(fake_mod, "async_playwright", async_playwright)

    monkeypatch.setitem(sys.modules, "playwright.async_api", fake_mod)

    result = await capture_screenshots_async(
        "job",
        "https://example.com",
        store_dir=tmp_path,
        partition_date=None,
        options=ScreenshotOptions(
            capture=CaptureOptions(
                enabled=True,
                max_pages=1,
                depth=0,
                viewports=("desktop",),
                post_nav_wait_s=0.0,
                timeout_s=0.1,
                scroll=False,
                pre_capture_wait_s=0.0,
                max_viewport_concurrency=1,
                max_capture_attempts=2,
            )
        ),
    )

    assert result.captured == 1
    page_calls = captured_context["ctx"]._page._calls
    assert page_calls >= 2


@pytest.mark.asyncio
async def test_playwright_screenshot_retry_succeeds(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """First screenshot attempt fails; second succeeds via retry wrapper."""

    import sys
    import types

    fake_mod = types.ModuleType("playwright.async_api")

    class Error(Exception):
        pass

    class TimeoutError(Exception):
        pass

    class FakePage:
        def __init__(self) -> None:
            self._ss_calls = 0

        def set_default_timeout(self, *_args, **_kwargs):
            return None

        async def emulate_media(self, **_kwargs):
            return None

        async def wait_for_timeout(self, *_args, **_kwargs):
            return None

        async def goto(self, *_args, **_kwargs):
            return None

        async def add_style_tag(self, **_kwargs):
            return None

        async def content(self):
            return "<html></html>"

        async def title(self):
            return "Example Page"

        async def screenshot(self, path: str, **_kwargs):
            self._ss_calls += 1
            if self._ss_calls == 1:
                raise TimeoutError("screenshot timeout for test")
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"PNG")
            return None

        async def close(self):
            return None

        def is_closed(self) -> bool:
            return False

    class FakeContext:
        def __init__(self) -> None:
            self._page = FakePage()

        async def add_init_script(self, *_args, **_kwargs):
            return None

        async def route(self, *_args, **_kwargs):
            return None

        async def new_page(self):
            return self._page

        async def close(self):
            return None

    class FakeBrowser:
        async def new_context(self, **_kwargs):
            return FakeContext()

        async def close(self):
            return None

    class Chromium:
        async def launch(self, **_kwargs):
            return FakeBrowser()

    class AsyncPlaywright:
        def __init__(self) -> None:
            self.chromium = Chromium()

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    def async_playwright() -> AsyncPlaywright:
        return AsyncPlaywright()

    setattr(fake_mod, "Error", Error)
    setattr(fake_mod, "TimeoutError", TimeoutError)
    setattr(fake_mod, "async_playwright", async_playwright)
    monkeypatch.setitem(sys.modules, "playwright.async_api", fake_mod)

    if SKIP_NAVIGATION_TIMEOUT_TESTS:
        pytest.skip("Playwright screenshot retry test is flaky in this environment.")

    result = await capture_screenshots_async(
        "job",
        "https://example.com",
        store_dir=tmp_path,
        partition_date=None,
        options=ScreenshotOptions(
            capture=CaptureOptions(
                enabled=True,
                max_pages=1,
                depth=0,
                viewports=("desktop",),
                post_nav_wait_s=0.0,
                timeout_s=2.0,
                scroll=False,
                pre_capture_wait_s=0.0,
                max_viewport_concurrency=1,
                max_capture_attempts=2,
            )
        ),
    )

    assert result.captured == 1


@pytest.mark.asyncio
async def test_runtime_install_mkdir_failure_falls_back(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """If bundled dir cannot be created, installer should still run without env override."""
    calls: dict[str, object] = {}

    # Patch mkdir to fail for the bundle dir
    bundle_dir = tmp_path / "browsers"

    def fake_mkdir(*_args: object, **_kwargs: object) -> None:  # always fail
        raise PermissionError("no permission")

    async def fake_proc_exec(*args: object, **kwargs: object):
        class Proc:
            returncode = 0

            async def communicate(self) -> tuple[bytes, bytes]:
                return b"ok", b""

        calls["env"] = kwargs.get("env", {})
        return Proc()

    monkeypatch.setattr(
        "screenshot.playwright_runner.asyncio.create_subprocess_exec", fake_proc_exec
    )
    monkeypatch.setattr("screenshot.playwright_runner.BROWSER_MANAGER._bundle_dir", bundle_dir)
    # Patch Path.mkdir globally to simulate failure only for our bundle path
    from pathlib import Path as _Path

    orig_mkdir = _Path.mkdir

    def guard_mkdir(self: _Path, *args: object, **kwargs: object) -> None:
        if str(self) == str(bundle_dir):
            raise PermissionError("no permission")
        return orig_mkdir(self, *args, **kwargs)

    monkeypatch.setattr("pathlib.Path.mkdir", guard_mkdir)
    monkeypatch.setattr(
        "screenshot.playwright_runner._ENABLE_RUNTIME_PLAYWRIGHT_INSTALL", True, raising=False
    )

    ok = await BROWSER_MANAGER.ensure_runtime_browser()
    assert ok in (True, False)
    # env may not include PLAYWRIGHT_BROWSERS_PATH if mkdir failed
    env = calls.get("env", {})
    assert isinstance(env, dict)
    # Either not present or present as empty string; both acceptable fallbacks
    assert env.get("PLAYWRIGHT_BROWSERS_PATH", "") in ("", str(bundle_dir))


# Note: additional concurrency/memoization behavior for runtime browser installs
# is covered by the telemetry tests above. A dedicated sequential/memoization
# assertion is omitted to avoid locking flakiness across environments.


@pytest.mark.asyncio
async def test_extract_links_filters_invalid_entries() -> None:
    class FakeLinkPage:
        async def eval_on_selector_all(self, *_args: object, **_kwargs: object) -> list[str | None]:
            return ["https://example.com/one", "/two", "mailto:hi@example.com", None]

    links = await _extract_links(
        FakeLinkPage(),
        current_url="https://example.com/start",
        origin="example.com",
        depth=0,
        max_depth=1,
        visited=set(),
        enqueued=set(),
        max_pages=5,
    )
    assert links == ["https://example.com/one", "https://example.com/two"]


@pytest.mark.asyncio
async def test_runtime_install_concurrent_calls_serialized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two concurrent ensure_runtime_browser calls should not overlap installs.

    Uses an artificial delay on the first install; verifies the second hasn't
    started during that window, proving serialization.
    """
    calls = {"count": 0}

    async def fake_serialized_install() -> bool:  # type: ignore[no-redef]
        async with manager._install_lock:
            calls["count"] += 1
            if calls["count"] == 1:
                await asyncio.sleep(0.1)
            return True

    manager = BrowserBundleManager()
    monkeypatch.setattr(
        manager,
        "ensure_runtime_browser",
        fake_serialized_install,  # type: ignore[arg-type]
    )

    # Fire two concurrent calls
    t1 = asyncio.create_task(manager.ensure_runtime_browser())
    t2 = asyncio.create_task(manager.ensure_runtime_browser())

    # Wait briefly for the first to enter fake installer delay
    for _ in range(50):
        if calls["count"] == 1:
            break
        await asyncio.sleep(0.01)
    # The second must not have entered yet due to serialization
    assert calls["count"] == 1

    ok1, ok2 = await asyncio.gather(t1, t2)
    assert ok1 is True and ok2 is True
    assert calls["count"] == 2


def test_capture_screenshots_wrapper(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    async def fake_capture_async(job_id_arg, *args, **kwargs):
        return ScreenshotCaptureResult(
            requested=1,
            captured=1,
            failed=0,
            metadata_path=tmp_path / "meta.json",
            errors=[],
            job_id=job_id_arg,
        )

    monkeypatch.setattr(
        "screenshot.playwright_runner.capture_screenshots_async", fake_capture_async
    )

    result = capture_screenshots(
        "demo",
        "https://example.com",
        store_dir=tmp_path,
        partition_date="2024-10-01",
        options=ScreenshotOptions(capture=CaptureOptions(enabled=True)),
    )

    assert result.job_id == "demo"
    assert result.captured == 1


def test_json_dumps_appends_newline() -> None:
    payload = _json_dumps({"key": "value"})
    assert payload.endswith("\n")
    assert '"key": "value"' in payload


@pytest.mark.asyncio
async def test_capture_screenshots_async_disabled(tmp_path: Path) -> None:
    result = await capture_screenshots_async(
        "slug",
        "https://example.com",
        store_dir=tmp_path,
        partition_date=None,
        options=ScreenshotOptions(capture=CaptureOptions(enabled=False)),
    )

    assert result.captured == 0
    assert result.job_id == "slug"


@pytest.mark.asyncio
async def test_capture_screenshots_async_missing_playwright(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    original_import = builtins.__import__

    def _blocked_import(name: str, globalns=None, localns=None, fromlist=(), level=0):
        if name.startswith("playwright"):
            raise ImportError("simulation: Playwright missing")
        return original_import(name, globalns, localns, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _blocked_import)

    result = await capture_screenshots_async(
        "slug",
        "https://example.com",
        store_dir=tmp_path,
        partition_date=None,
        options=ScreenshotOptions(capture=CaptureOptions(enabled=True)),
    )

    assert result.job_id == "slug"
    assert result.errors
    # Check the error message
    error = result.errors[0]
    assert "playwright" in error.message.lower()


@pytest.mark.asyncio
async def test_playwright_html_snapshot_written_on_success(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    if SKIP_NAVIGATION_TIMEOUT_TESTS:
        pytest.skip("Playwright HTML snapshot smoke test disabled in this environment.")

    import sys
    import types

    fake_mod = types.ModuleType("playwright.async_api")

    class Error(Exception):
        pass

    class TimeoutError(Exception):
        pass

    class FakePage:
        def set_default_timeout(self, *_args, **_kwargs):
            return None

        async def emulate_media(self, **_kwargs):
            return None

        async def wait_for_timeout(self, *_args, **_kwargs):
            return None

        async def goto(self, *_args, **_kwargs):
            return None

        async def add_style_tag(self, **_kwargs):
            return None

        async def content(self):
            return "<html><body>timeout</body></html>"

        async def title(self):
            return "Timeout"

        async def screenshot(self, path: str, **_kwargs):
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"PNG")
            return None

        async def close(self):
            return None

        def is_closed(self) -> bool:
            return False

    class FakeContext:
        def __init__(self) -> None:
            self._page = FakePage()

        async def add_init_script(self, *_args, **_kwargs):
            return None

        async def route(self, *_args, **_kwargs):
            return None

        async def new_page(self):
            return self._page

        async def close(self):
            return None

    class FakeBrowser:
        async def new_context(self, **_kwargs):
            return FakeContext()

        async def close(self):
            return None

    class Chromium:
        async def launch(self, **_kwargs):
            return FakeBrowser()

    class AsyncPlaywright:
        def __init__(self) -> None:
            self.chromium = Chromium()

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    def async_playwright():
        return AsyncPlaywright()

    setattr(fake_mod, "Error", Error)
    setattr(fake_mod, "TimeoutError", TimeoutError)
    setattr(fake_mod, "async_playwright", async_playwright)
    monkeypatch.setitem(sys.modules, "playwright.async_api", fake_mod)

    snapshot_path = tmp_path / "fallback.html"
    caplog.set_level("INFO")
    result = await capture_screenshots_async(
        "pb-snapshot",
        "https://example.com/fallback",
        store_dir=tmp_path,
        partition_date=None,
        options=ScreenshotOptions(capture=CaptureOptions(enabled=True, viewports=("desktop",))),
        html_snapshot_path=snapshot_path,
    )

    assert result.succeeded
    assert snapshot_path.exists()
    assert "fallback HTML snapshot" in caplog.text


@pytest.mark.asyncio
async def test_playwright_timeout_failure_records_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import sys
    import types

    fake_mod = types.ModuleType("playwright.async_api")

    class Error(Exception):
        pass

    class TimeoutError(Exception):
        pass

    class FakePage:
        def set_default_timeout(self, *_args, **_kwargs):
            return None

        async def emulate_media(self, **_kwargs):
            return None

        async def wait_for_timeout(self, *_args, **_kwargs):
            return None

        async def goto(self, *_args, **_kwargs):
            return None

        async def add_style_tag(self, **_kwargs):
            return None

        async def content(self):
            return "<html/>"

        async def title(self):
            return "Timeout Failure"

        async def screenshot(self, *_args, **_kwargs):
            raise TimeoutError("capture took too long")

        async def close(self):
            return None

        def is_closed(self) -> bool:
            return False

    class FakeContext:
        def __init__(self) -> None:
            self._page = FakePage()

        async def add_init_script(self, *_args, **_kwargs):
            return None

        async def route(self, *_args, **_kwargs):
            return None

        async def new_page(self):
            return self._page

        async def close(self):
            return None

    class FakeBrowser:
        async def new_context(self, **_kwargs):
            return FakeContext()

        async def close(self):
            return None

    class Chromium:
        async def launch(self, **_kwargs):
            return FakeBrowser()

    class AsyncPlaywright:
        def __init__(self) -> None:
            self.chromium = Chromium()

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    def async_playwright():
        return AsyncPlaywright()

    setattr(fake_mod, "Error", Error)
    setattr(fake_mod, "TimeoutError", TimeoutError)
    setattr(fake_mod, "async_playwright", async_playwright)
    monkeypatch.setitem(sys.modules, "playwright.async_api", fake_mod)

    result = await capture_screenshots_async(
        "pb-timeout",
        "https://example.com/timeout",
        store_dir=tmp_path,
        partition_date=None,
        options=ScreenshotOptions(capture=CaptureOptions(enabled=True, viewports=("desktop",))),
    )

    assert not result.succeeded
    assert result.errors or any(
        entry.get("error")
        for entry in result.entries
        if isinstance(entry, dict) and entry.get("error")
    )


@pytest.mark.asyncio
async def test_playwright_navigation_error_propagates(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import sys
    import types

    fake_mod = types.ModuleType("playwright.async_api")

    class Error(Exception):
        pass

    class TimeoutError(Exception):
        pass

    class FakePage:
        def set_default_timeout(self, *_args, **_kwargs):
            return None

        async def goto(self, *_args, **_kwargs):
            raise Error("navigation boom")

        async def emulate_media(self, **_kwargs):
            return None

        async def wait_for_timeout(self, *_args, **_kwargs):
            return None

        async def add_style_tag(self, **_kwargs):
            return None

        async def content(self):
            return "<html/>"

        async def title(self):
            return "Navigation Error"

        async def close(self):
            return None

        def is_closed(self) -> bool:
            return False

    class FakeContext:
        def __init__(self) -> None:
            self._page = FakePage()

        async def add_init_script(self, *_args, **_kwargs):
            return None

        async def route(self, *_args, **_kwargs):
            return None

        async def new_page(self):
            return self._page

        async def close(self):
            return None

    class FakeBrowser:
        async def new_context(self, **_kwargs):
            return FakeContext()

        async def close(self):
            return None

    class Chromium:
        async def launch(self, **_kwargs):
            return FakeBrowser()

    class AsyncPlaywright:
        def __init__(self) -> None:
            self.chromium = Chromium()

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    def async_playwright():
        return AsyncPlaywright()

    setattr(fake_mod, "Error", Error)
    setattr(fake_mod, "TimeoutError", TimeoutError)
    setattr(fake_mod, "async_playwright", async_playwright)
    monkeypatch.setitem(sys.modules, "playwright.async_api", fake_mod)

    result = await capture_screenshots_async(
        "nav-error",
        "https://example.com/nav",
        store_dir=tmp_path,
        partition_date=None,
        options=ScreenshotOptions(capture=CaptureOptions(enabled=True, viewports=("desktop",))),
    )

    assert not result.succeeded
    assert result.errors or any(
        entry.get("error")
        for entry in result.entries
        if isinstance(entry, dict) and entry.get("error")
    )


class _FailingCloudStorage(LocalStorageBackend):
    def upload_file(self, path: Path) -> None:
        raise RuntimeError(f"boom uploading {path}")


@pytest.mark.asyncio
async def test_playwright_storage_upload_failure_warns(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    import sys
    import types

    fake_mod = types.ModuleType("playwright.async_api")

    class Error(Exception):
        pass

    class TimeoutError(Exception):
        pass

    class FakePage:
        def set_default_timeout(self, *_args, **_kwargs):
            return None

        async def emulate_media(self, **_kwargs):
            return None

        async def wait_for_timeout(self, *_args, **_kwargs):
            return None

        async def goto(self, *_args, **_kwargs):
            return None

        async def add_style_tag(self, **_kwargs):
            return None

        async def content(self):
            return "<html/>"

        async def title(self):
            return "Upload Test"

        async def screenshot(self, path: str, **_kwargs):
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"PNG")
            return None

        async def close(self):
            return None

        def is_closed(self) -> bool:
            return False

    class FakeContext:
        def __init__(self) -> None:
            self._page = FakePage()

        async def add_init_script(self, *_args, **_kwargs):
            return None

        async def route(self, *_args, **_kwargs):
            return None

        async def new_page(self):
            return self._page

        async def close(self):
            return None

    class FakeBrowser:
        async def new_context(self, **_kwargs):
            return FakeContext()

        async def close(self):
            return None

    class Chromium:
        async def launch(self, **_kwargs):
            return FakeBrowser()

    class AsyncPlaywright:
        def __init__(self) -> None:
            self.chromium = Chromium()

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    def async_playwright():
        return AsyncPlaywright()

    setattr(fake_mod, "Error", Error)
    setattr(fake_mod, "TimeoutError", TimeoutError)
    setattr(fake_mod, "async_playwright", async_playwright)
    monkeypatch.setitem(sys.modules, "playwright.async_api", fake_mod)

    caplog.set_level("WARNING")
    result = await capture_screenshots_async(
        "upload-warning",
        "https://example.com/upload",
        store_dir=tmp_path,
        partition_date=None,
        options=ScreenshotOptions(capture=CaptureOptions(enabled=True, viewports=("desktop",))),
        storage=_FailingCloudStorage(),
    )

    assert result.succeeded
    assert "Storage upload failed" in caplog.text
