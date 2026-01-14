from pathlib import Path
from typing import NoReturn

import pytest

from screenshot._models_plans import BrowserPlan, CapturePlan, RunnerPlan
from screenshot.models import ScreenshotOptions
from screenshot.selenium_runner import (
    _apply_browser_mutations,
    _capture_full_page,
    _capture_url_with_viewports,
    _collect_links,
    _failed_entry,
    _scroll_page,
    _SeleniumImportError,
    capture_screenshots_async,
)


@pytest.mark.asyncio
async def test_selenium_runner_missing_dependency(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _raise() -> NoReturn:
        raise _SeleniumImportError("Selenium backend unavailable")

    monkeypatch.setattr("screenshot.selenium_runner._load_selenium_modules", _raise)

    result = await capture_screenshots_async(
        "test-job",
        "https://example.com",
        store_dir=tmp_path,
        partition_date=None,
        options=ScreenshotOptions(),
        html_snapshot_path=None,
        cancel_token=None,
        storage=None,
    )

    assert result.requested == 0
    assert result.captured == 0
    assert result.failed == 0
    assert result.errors and "Selenium backend unavailable" in result.errors[0].message


@pytest.mark.asyncio
async def test_selenium_navigation_retry_logs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level("DEBUG")

    # Build fakes returned by _load_selenium_modules()
    class TimeoutException(Exception):
        pass

    class WebDriverException(Exception):
        pass

    class Options:
        def __init__(self) -> None:
            self.binary_location = None

        def add_argument(self, *_args: object) -> None:
            return None

    class _Driver:
        def __init__(self) -> None:
            self._calls = 0
            self.title = "ok"

        def set_page_load_timeout(self, _timeout: object) -> None:
            return None

        def get(self, _url: object) -> None:
            # Fail first call with timeout, then succeed
            self._calls += 1
            if self._calls == 1:
                raise TimeoutException("nav timeout")
            return None

        def execute_cdp_cmd(self, *_args: object, **_kwargs: object) -> dict[str, str]:
            # Return values used by full-page capture path if invoked
            return {"data": ""}

        def get_screenshot_as_png(self) -> bytes:
            return b"PNG"

        @property
        def page_source(self) -> str:
            return "<html/>"

        def quit(self) -> None:
            return None

    class webdriver:
        @staticmethod
        def Chrome(*_args: object, **_kwargs: object) -> _Driver:
            return _Driver()

    def _fake_loader() -> (
        tuple[type[webdriver], type[Options], type[TimeoutException], type[WebDriverException]]
    ):
        return webdriver, Options, TimeoutException, WebDriverException

    monkeypatch.setattr("screenshot.selenium_runner._load_selenium_modules", _fake_loader)

    res = await capture_screenshots_async(
        "job",
        "https://example.com",
        store_dir=tmp_path,
        partition_date=None,
        options=ScreenshotOptions(),
        html_snapshot_path=None,
        cancel_token=None,
        storage=None,
    )

    assert res.captured >= 1
    # Ensure our retry logging hook fired
    assert "Retrying navigation (selenium)" in caplog.text


def test_apply_browser_mutations_executes_optional_scripts() -> None:
    executed: list[str] = []

    class Driver:
        def execute_script(self, script: str, *args: object) -> None:
            executed.append(script)

    browser_plan = BrowserPlan(
        allow_autoplay=True,
        hide_overlays=True,
        reduced_motion=True,
        disable_animations=True,
        mute_media=True,
        block_media=False,
        compatibility_level="low",
        user_agent="UA",
    )
    runner_plan = RunnerPlan(
        extra_styles=("body {color:red;}",),
        extra_init_scripts=("console.log('init');",),
        navigation_strategies=(),
        playwright_executable_path=None,
        extra={},
    )

    _apply_browser_mutations(Driver(), browser_plan, runner_plan)

    assert any("autoplay" in script.lower() for script in executed)
    assert any("hide-overlays" in script for script in executed)
    assert any("disable-animations" in script for script in executed)
    assert any("console.log('init');" in script for script in executed)


def test_scroll_page_and_collect_links(monkeypatch: pytest.MonkeyPatch) -> None:
    heights = [100, 120, 120]

    class Driver:
        def __init__(self) -> None:
            self._scroll_calls = 0

        def execute_script(self, script: str, *args: object) -> int | bool | None:
            if "Math.max" in script:
                value = heights[min(self._scroll_calls, len(heights) - 1)]
                self._scroll_calls += 1
                return value
            if "window.scrollY" in script:
                return True
            return None

    monkeypatch.setattr("time.sleep", lambda _seconds: None)
    driver = Driver()
    scroll_height = _scroll_page(driver, max_steps=3, delay_ms=10)
    assert scroll_height == heights[-1]

    class LinkDriver:
        def execute_script(self, *_args: object) -> list[str | None]:
            return ["https://example.com/a", "/b", "mailto:test@example.com", None]

    links = _collect_links(
        driver=LinkDriver(),
        current_url="https://example.com",
        origin="example.com",
        depth=0,
        max_depth=1,
        max_pages=5,
    )
    assert links == ["https://example.com/a", "https://example.com/b"]


def test_failed_entry_structure() -> None:
    entry = _failed_entry(2, 1, "desktop", "https://example.com", 10.0, "boom")
    assert entry["index"] == 2
    assert entry["status"] == "failed"
    assert entry["timeout_seconds"] == 10.0


def test_capture_url_handles_driver_init_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    capture_plan = CapturePlan(
        max_pages=1,
        depth=0,
        delay_ms=0,
        viewport_specs={"desktop": {"viewport": {"width": 100, "height": 50}}},
        viewport_details=[
            {
                "name": "desktop",
                "width": 100,
                "height": 50,
                "device_scale_factor": 1.0,
                "is_mobile": False,
            }
        ],
        primary_viewport="desktop",
        timeout_sec=5.0,
        max_total_duration_sec=5.0,
        max_capture_attempts=1,
        max_viewport_concurrency=1,
        scroll_enabled=False,
        scroll_step_delay_ms=250,
        max_scroll_steps=15,
        full_page_capture=False,
        settle_timeout_ms=0,
    )
    browser_plan = BrowserPlan(
        allow_autoplay=False,
        hide_overlays=False,
        reduced_motion=False,
        disable_animations=False,
        mute_media=False,
        block_media=False,
        compatibility_level="low",
        user_agent=None,
    )
    runner_plan = RunnerPlan(
        extra_styles=(),
        extra_init_scripts=(),
        navigation_strategies=(),
        playwright_executable_path=None,
        extra={},
    )

    def fake_create_driver(**_kwargs: object) -> NoReturn:
        raise RuntimeError("boom")

    monkeypatch.setattr("screenshot.selenium_runner._create_driver", fake_create_driver)

    class DummyWebdriver:
        pass

    class DummyOptions:
        pass

    outcome = _capture_url_with_viewports(
        webdriver=DummyWebdriver,
        Options=DummyOptions,
        TimeoutException=RuntimeError,
        WebDriverException=RuntimeError,
        job_id="job",
        url="https://example.com",
        origin="example.com",
        depth=0,
        capture_plan=capture_plan,
        browser_plan=browser_plan,
        runner_plan=runner_plan,
        screenshot_dir=tmp_path,
        page_index=0,
        snapshot_path=None,
        snapshot_written=False,
    )

    assert outcome.failed == 1
    assert outcome.errors and outcome.errors[0].error_type == "driver_init"


def test_capture_url_uses_scroll_tuning(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    recorded: dict[str, int] = {}

    def fake_scroll_page(_driver: object, *, max_steps: int, delay_ms: int) -> int:
        recorded["max_steps"] = max_steps
        recorded["delay_ms"] = delay_ms
        return 200

    monkeypatch.setattr("screenshot.selenium_runner._scroll_page", fake_scroll_page)

    class FakeDriver:
        title = "Fake"

        def set_page_load_timeout(self, *_args: object, **_kwargs: object) -> None:
            return None

        def get(self, *_args: object, **_kwargs: object) -> None:
            return None

        def execute_script(self, *_args: object, **_kwargs: object) -> int:
            return 0

        def get_screenshot_as_png(self) -> bytes:
            return b"PNG"

        def quit(self) -> None:
            return None

    def fake_create_driver(**_kwargs: object) -> tuple[FakeDriver, None]:
        return FakeDriver(), None

    monkeypatch.setattr("screenshot.selenium_runner._create_driver", fake_create_driver)

    capture_plan = CapturePlan(
        max_pages=1,
        depth=0,
        delay_ms=0,
        viewport_specs={"desktop": {"viewport": {"width": 100, "height": 50}}},
        viewport_details=[
            {
                "name": "desktop",
                "width": 100,
                "height": 50,
                "device_scale_factor": 1.0,
                "is_mobile": False,
            }
        ],
        primary_viewport="desktop",
        timeout_sec=5.0,
        max_total_duration_sec=5.0,
        max_capture_attempts=1,
        max_viewport_concurrency=1,
        scroll_enabled=True,
        scroll_step_delay_ms=155,
        max_scroll_steps=6,
        full_page_capture=False,
        settle_timeout_ms=0,
    )
    browser_plan = BrowserPlan(
        allow_autoplay=False,
        hide_overlays=False,
        reduced_motion=False,
        disable_animations=False,
        mute_media=False,
        block_media=False,
        compatibility_level="low",
        user_agent=None,
    )
    runner_plan = RunnerPlan(
        extra_styles=(),
        extra_init_scripts=(),
        navigation_strategies=(),
        playwright_executable_path=None,
        extra={},
    )

    class DummyWebdriver:
        pass

    class DummyOptions:
        pass

    outcome = _capture_url_with_viewports(
        webdriver=DummyWebdriver,
        Options=DummyOptions,
        TimeoutException=RuntimeError,
        WebDriverException=RuntimeError,
        job_id="job",
        url="https://example.com",
        origin="example.com",
        depth=0,
        capture_plan=capture_plan,
        browser_plan=browser_plan,
        runner_plan=runner_plan,
        screenshot_dir=tmp_path,
        page_index=0,
        snapshot_path=None,
        snapshot_written=False,
    )

    assert outcome.captured == 1
    assert recorded == {"max_steps": 6, "delay_ms": 155}


def test_selenium_timings_emitted_when_enabled(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SCREENSHOT_ENABLE_TIMING", "1")
    monkeypatch.setattr("screenshot.selenium_runner.ENABLE_TIMING", True)

    class FakeDriver:
        title = "Fake"

        def set_page_load_timeout(self, *_args: object, **_kwargs: object) -> None:
            return None

        def get(self, *_args: object, **_kwargs: object) -> None:
            return None

        def execute_script(self, *_args: object, **_kwargs: object) -> None:
            return None

        def get_screenshot_as_png(self) -> bytes:
            return b"PNG"

        def quit(self) -> None:
            return None

    def fake_create_driver(**_kwargs: object) -> tuple[FakeDriver, None]:
        return FakeDriver(), None

    monkeypatch.setattr("screenshot.selenium_runner._create_driver", fake_create_driver)

    capture_plan = CapturePlan(
        max_pages=1,
        depth=0,
        delay_ms=0,
        viewport_specs={"desktop": {"viewport": {"width": 100, "height": 50}}},
        viewport_details=[
            {
                "name": "desktop",
                "width": 100,
                "height": 50,
                "device_scale_factor": 1.0,
                "is_mobile": False,
            }
        ],
        primary_viewport="desktop",
        timeout_sec=5.0,
        max_total_duration_sec=5.0,
        max_capture_attempts=1,
        max_viewport_concurrency=1,
        scroll_enabled=False,
        scroll_step_delay_ms=250,
        max_scroll_steps=15,
        full_page_capture=False,
        settle_timeout_ms=0,
    )
    browser_plan = BrowserPlan(
        allow_autoplay=False,
        hide_overlays=False,
        reduced_motion=False,
        disable_animations=False,
        mute_media=False,
        block_media=False,
        compatibility_level="low",
        user_agent=None,
    )
    runner_plan = RunnerPlan(
        extra_styles=(),
        extra_init_scripts=(),
        navigation_strategies=(),
        playwright_executable_path=None,
        extra={},
    )

    class DummyWebdriver:
        pass

    class DummyOptions:
        pass

    outcome = _capture_url_with_viewports(
        webdriver=DummyWebdriver,
        Options=DummyOptions,
        TimeoutException=RuntimeError,
        WebDriverException=RuntimeError,
        job_id="job",
        url="https://example.com",
        origin="example.com",
        depth=0,
        capture_plan=capture_plan,
        browser_plan=browser_plan,
        runner_plan=runner_plan,
        screenshot_dir=tmp_path,
        page_index=0,
        snapshot_path=None,
        snapshot_written=False,
    )

    assert outcome.captured == 1
    assert outcome.entries
    timings = outcome.entries[0].get("timings")
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


def test_capture_full_page_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class Driver:
        def __init__(self) -> None:
            self._scripts: list[str] = []

        def execute_cdp_cmd(self, *_args: object, **_kwargs: object) -> None:
            raise RuntimeError("cdp unsupported")

        def get_screenshot_as_png(self) -> bytes:
            return b"FAKEPNG"

        def execute_script(self, *_args: object, **_kwargs: object) -> int:
            return 200

    out_path = tmp_path / "shot.png"
    _capture_full_page(
        Driver(),
        {"viewport": {"width": 120, "height": 80}, "device_scale_factor": 1.0},
        out_path,
    )
    assert out_path.exists()
