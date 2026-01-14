"""Selenium-backed screenshot capture pipeline.

This module mirrors the Playwright implementation but swaps in Selenium +
Chromium. It reuses the sanitised capture plans, applies the same browser
mutations, and streams artifacts through the shared storage backend so the
CLI and worker surfaces can switch between engines transparently. The path
is a safety valve whenever Playwright is unavailable or a Selenium-specific
feature (such as bespoke CDP commands) is required.

Example:
    >>> import asyncio
    >>> from pathlib import Path
    >>> from screenshot.models import CaptureOptions, ScreenshotOptions
    >>> opts = ScreenshotOptions(capture=CaptureOptions(enabled=True))
    >>> asyncio.run(
    ...     capture_screenshots_async(
    ...         "demo",
    ...         source_url="https://example.com",
    ...         store_dir=Path("/tmp/screens"),
    ...         partition_date=None,
    ...         options=opts,
    ...         job_id="demo",
    ...     )
    ... )
"""

from __future__ import annotations

import asyncio
import base64
import logging
import math
import tempfile
import time
from collections import deque
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from infra_core.logging_utils import sanitize_url
from infra_core.retry import (
    AsyncRetryConfig,
    RetryCallState,
    retry_state_summary,
    run_with_retries_sync,
)

from ._models_plans import BrowserPlan, CapturePlan, RunnerPlan
from ._shared.errors import ScreenshotError, make_error
from ._shared.storage import AsyncStorageBackend, CloudStorageBackend, StorageBackend
from ._shared.url import normalize_url
from .defaults import DEFAULTS
from .models import ScreenshotCaptureResult, ScreenshotOptions
from .playwright_runner import (  # Reuse shared sanitisation + helpers
    AUTOPLAY_INIT_SCRIPT,
    DEFAULT_STORAGE,
    DISABLE_ANIMATIONS_STYLE,
    HIDE_OVERLAY_STYLE,
    MUTE_MEDIA_INIT_SCRIPT,
    REDUCED_MOTION_MATCH_MEDIA_SCRIPT,
    CancellationToken,
    _build_filename,
    _sanitize_options,
    utc_now_iso,
)

logger = logging.getLogger(__name__)

SCROLL_STEP_DELAY_MS = DEFAULTS.scroll_step_delay_ms
MAX_SCROLL_STEPS = DEFAULTS.max_scroll_steps
ENABLE_TIMING = DEFAULTS.enable_timing


class _SeleniumImportError(RuntimeError):
    """Marker exception used when selenium is not installed."""


def _load_selenium_modules() -> tuple[Any, type[Any], type[BaseException], type[BaseException]]:
    try:
        from selenium import webdriver
        from selenium.common.exceptions import TimeoutException, WebDriverException
        from selenium.webdriver.chrome.options import Options
    except ImportError as exc:  # pragma: no cover - depends on optional dep
        raise _SeleniumImportError(
            "Selenium backend requires optional dependency 'selenium'; "
            "install via `pip install infra-screenshot[selenium]`."
        ) from exc

    return webdriver, Options, TimeoutException, WebDriverException


async def capture_screenshots_async(
    job_id: str,
    source_url: str,
    *,
    store_dir: Path,
    partition_date: str | None,
    options: ScreenshotOptions,
    html_snapshot_path: Path | None = None,
    cancel_token: CancellationToken | None = None,
    storage: StorageBackend | None = None,
) -> ScreenshotCaptureResult:
    """Capture rendered screenshots for a site using Selenium + Chromium.

    Args:
        job_id: Stable identifier that ties output files back to the calling job.
        source_url: Initial URL to load and capture.
        store_dir: Root directory where assets/metadata partitions are written.
        partition_date: Optional YYYY-MM-DD partition inserted into metadata outputs.
        options: Fully populated `ScreenshotOptions` describing capture plans.
        html_snapshot_path: Optional path where the raw HTML should be persisted.
        cancel_token: Cooperative cancellation hook exposing `raise_if_cancelled`.
        storage: Custom storage backend used for writes/uploads; defaults to local.

    Returns:
        `ScreenshotCaptureResult` summarising captured entries, metadata locations,
        and structured errors suitable for logging or retry decisions.

    Example:
        >>> import asyncio
        >>> from pathlib import Path
        >>> from screenshot.models import CaptureOptions, ScreenshotOptions
        >>> opts = ScreenshotOptions(capture=CaptureOptions(enabled=True))
        >>> asyncio.run(
        ...     capture_screenshots_async(
        ...         "demo",
        ...         source_url="https://example.com",
        ...         store_dir=Path("/tmp/screens"),
        ...         partition_date=None,
        ...         options=opts,
        ...     )
        ... )
    """

    job_identifier = job_id

    storage_backend = storage or DEFAULT_STORAGE

    try:
        webdriver, Options, TimeoutException, WebDriverException = _load_selenium_modules()
    except _SeleniumImportError as exc:
        logger.error("Selenium backend unavailable: %s", exc)
        return ScreenshotCaptureResult(
            requested=0,
            captured=0,
            failed=0,
            metadata_path=None,
            entries=[],
            errors=[make_error("dependency", str(exc), retryable=True)],
            job_id=job_identifier,
        )

    plans = _sanitize_options(options)
    capture_plan = plans.capture
    browser_plan = plans.browser
    runner_plan = plans.runner

    site_dir = (store_dir or Path(".")) / job_identifier
    screenshot_dir = site_dir / "assets" / "screenshots"
    metadata_dir = site_dir / "metadata"
    storage_backend.ensure_parent(screenshot_dir / "placeholder")
    storage_backend.ensure_parent(metadata_dir / "screenshots.json")

    def _check_cancel() -> None:
        if cancel_token is not None:
            cancel_token.raise_if_cancelled()

    def _run_capture_sync() -> ScreenshotCaptureResult:
        requested = 0
        captured = 0
        failed = 0
        entries: list[dict[str, Any]] = []
        errors: list[ScreenshotError] = []
        snapshot_written = html_snapshot_path.exists() if html_snapshot_path else False

        normalized_start = _normalize_url(source_url)
        parsed_start = urlparse(normalized_start)
        if parsed_start.scheme not in ("http", "https"):
            message = f"unsupported scheme for screenshot capture: {normalized_start}"
            logger.warning("Skipping screenshot capture for job_id %s; %s", job_identifier, message)
            return ScreenshotCaptureResult(
                requested=0,
                captured=0,
                failed=0,
                metadata_path=None,
                entries=[],
                errors=[make_error("validation", message, details={"url": normalized_start})],
                job_id=job_identifier,
            )

        origin = parsed_start.netloc
        queue: deque[tuple[str, int]] = deque([(normalized_start, 0)])
        visited: set[str] = set()
        enqueued: set[str] = {normalized_start}

        start_time = time.monotonic()
        max_total_duration = capture_plan.max_total_duration_sec or (
            capture_plan.timeout_sec * capture_plan.max_pages
        )

        while queue and len(visited) < capture_plan.max_pages:
            _check_cancel()
            elapsed = time.monotonic() - start_time
            if elapsed >= max_total_duration:
                warning = f"budget exceeded after {elapsed:.1f}s (budget {max_total_duration:.1f}s)"
                logger.warning(
                    "Screenshot capture budget exceeded for job_id %s; stopping", job_identifier
                )
                errors.append(
                    make_error(
                        "budget_exceeded",
                        warning,
                        details={"elapsed_seconds": elapsed, "budget_seconds": max_total_duration},
                    )
                )
                break

            current_url, depth = queue.popleft()
            if current_url in visited:
                continue
            visited.add(current_url)
            requested += 1

            new_links: list[str] = []
            page_index = len(entries)
            try:
                capture_result = _capture_url_with_viewports(
                    webdriver=webdriver,
                    Options=Options,
                    TimeoutException=TimeoutException,
                    WebDriverException=WebDriverException,
                    job_id=job_identifier,
                    url=current_url,
                    origin=origin,
                    depth=depth,
                    capture_plan=capture_plan,
                    browser_plan=browser_plan,
                    runner_plan=runner_plan,
                    screenshot_dir=screenshot_dir,
                    page_index=page_index,
                    snapshot_path=html_snapshot_path if html_snapshot_path else None,
                    snapshot_written=snapshot_written,
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception(
                    "Unexpected Selenium failure for job_id %s (%s)",
                    job_identifier,
                    sanitize_url(current_url),
                )
                entry = {
                    "index": page_index,
                    "url": current_url,
                    "depth": depth,
                    "viewport": capture_plan.primary_viewport,
                    "status": "failed",
                    "title": None,
                    "scroll_height": None,
                    "screenshot_path": None,
                    "error": str(exc),
                    "navigation_strategy": None,
                    "timeout_seconds": capture_plan.timeout_sec,
                    "attempts": 1,
                    "attempt_timeout_seconds": capture_plan.timeout_sec,
                }
                entries.append(entry)
                failed += 1
                errors.append(make_error("unexpected_failure", str(exc), retryable=True))
                continue

            entries.extend(capture_result.entries)
            captured += capture_result.captured
            failed += capture_result.failed
            if capture_result.errors:
                errors.extend(capture_result.errors)
            if capture_result.new_links:
                new_links = capture_result.new_links
            if capture_result.snapshot_written:
                snapshot_written = True

            if new_links:
                remaining_capacity = max(
                    0,
                    capture_plan.max_pages - len(visited) - len(queue),
                )
                for link in new_links:
                    if remaining_capacity <= 0:
                        break
                    if link in visited or link in enqueued:
                        continue
                    queue.append((link, depth + 1))
                    enqueued.add(link)
                    remaining_capacity -= 1

        metadata = {
            "schema_version": "screenshot_capture/v1",
            "job_id": job_identifier,
            "source_url": source_url,
            "fetched_at": utc_now_iso(),
            "options": plans.to_dict(),
            "entries": entries,
            "errors": [error.to_dict() for error in errors],
        }
        metadata_path = metadata_dir / "screenshots.json"
        storage_backend.write_json(metadata_path, metadata)

        return ScreenshotCaptureResult(
            requested=requested,
            captured=captured,
            failed=failed,
            metadata_path=metadata_path,
            entries=entries,
            errors=errors,
            job_id=job_identifier,
        )

    loop_result = await asyncio.to_thread(_run_capture_sync)

    if loop_result.metadata_path is not None:
        if isinstance(storage_backend, AsyncStorageBackend):
            await storage_backend.upload_file_async(loop_result.metadata_path)
        elif isinstance(storage_backend, CloudStorageBackend):
            await asyncio.to_thread(storage_backend.upload_file, loop_result.metadata_path)

    return loop_result


class _CaptureOutcome:
    __slots__ = ("entries", "captured", "failed", "errors", "new_links", "snapshot_written")

    def __init__(
        self,
        entries: list[dict[str, Any]],
        captured: int,
        failed: int,
        errors: list[ScreenshotError],
        new_links: list[str],
        snapshot_written: bool,
    ) -> None:
        self.entries = entries
        self.captured = captured
        self.failed = failed
        self.errors = errors
        self.new_links = new_links
        self.snapshot_written = snapshot_written


def _capture_url_with_viewports(
    *,
    webdriver: Any,
    Options: type[Any],
    TimeoutException: type[BaseException],
    WebDriverException: type[BaseException],
    job_id: str,
    url: str,
    origin: str,
    depth: int,
    capture_plan: CapturePlan,
    browser_plan: BrowserPlan,
    runner_plan: RunnerPlan,
    screenshot_dir: Path,
    page_index: int,
    snapshot_path: Path | None,
    snapshot_written: bool,
) -> _CaptureOutcome:
    """Capture a single URL across the configured viewport presets.

    Returns:
        `_CaptureOutcome` containing per-viewport entries, structured errors,
        any discovered follow-up links, and whether an HTML snapshot was created.
    """
    safe_url = sanitize_url(url)
    viewport_names = list(capture_plan.viewport_specs.keys())
    if not viewport_names:
        viewport_names = [capture_plan.primary_viewport]

    entries: list[dict[str, Any]] = []
    captured = 0
    failed = 0
    error_messages: list[ScreenshotError] = []
    new_links: list[str] = []

    for viewport_name in viewport_names:
        spec = (
            capture_plan.viewport_specs.get(viewport_name)
            or capture_plan.viewport_specs[capture_plan.primary_viewport]
        )
        is_primary = viewport_name == capture_plan.primary_viewport
        timing_payload: dict[str, float] | None = None

        driver = None
        temp_profile: tempfile.TemporaryDirectory[str] | None = None
        try:
            driver, temp_profile = _create_driver(
                webdriver=webdriver,
                Options=Options,
                WebDriverException=WebDriverException,
                viewport_spec=spec,
                browser_plan=browser_plan,
                runner_plan=runner_plan,
            )
        except Exception as exc:
            logger.exception(
                "Failed to start Selenium driver for job_id %s (%s)", job_id, viewport_name
            )
            entry = _failed_entry(
                page_index,
                depth,
                viewport_name,
                url,
                capture_plan.timeout_sec,
                str(exc),
            )
            entries.append(entry)
            failed += 1
            error_messages.append(make_error("driver_init", str(exc), retryable=True))
            continue

        try:
            driver.set_page_load_timeout(max(1, math.ceil(capture_plan.timeout_sec)))

            drv = driver
            if drv is None:  # defensive, helps type checkers
                raise RuntimeError("Selenium driver not initialized")

            timings: dict[str, float] | None = {} if ENABLE_TIMING else None
            attempt_start = time.monotonic()

            def _elapsed_ms(start: float) -> float:
                return round((time.monotonic() - start) * 1000.0, 3)

            def _navigate_once() -> None:
                drv.get(url)

            def _should_retry(exc: BaseException) -> bool:
                # Retry typical transient navigation errors/timeouts
                msg = str(exc).lower()
                return (
                    isinstance(exc, TimeoutException)
                    or (hasattr(exc, "msg") and "timeout" in msg)
                    or ("net::err_" in msg)
                    or ("navigation" in msg)
                )

            config = AsyncRetryConfig.create(
                max_retries=max(0, capture_plan.max_capture_attempts - 1),
                backoff=0.5,
                max_backoff=min(5.0, float(capture_plan.timeout_sec)),
            )

            def _before_sleep(state: RetryCallState) -> None:
                exc, wait_time, _ = retry_state_summary(state)
                logger.debug(
                    "Retrying navigation (selenium) job_id=%s viewport=%s url=%s "
                    "after %.2fs due to: %s",
                    job_id,
                    viewport_name,
                    safe_url,
                    (wait_time or 0.0),
                    exc,
                )

            nav_start = time.monotonic()
            run_with_retries_sync(
                operation=_navigate_once,
                config=config,
                should_retry=_should_retry,
                before_sleep=_before_sleep,
            )
            if timings is not None:
                timings["navigation_ms"] = _elapsed_ms(nav_start)
            style_start = time.monotonic()
            _apply_browser_mutations(driver, browser_plan, runner_plan)
            if timings is not None:
                timings["style_ms"] = _elapsed_ms(style_start)
            delay = max(0, capture_plan.delay_ms) / 1000.0
            if delay:
                delay_start = time.monotonic()
                time.sleep(delay)
                if timings is not None:
                    timings["post_nav_wait_ms"] = _elapsed_ms(delay_start)
            settle_timeout_ms = capture_plan.settle_timeout_ms
            scroll_height = None
            if capture_plan.scroll_enabled:
                scroll_start = time.monotonic()
                scroll_height = _scroll_page(
                    driver,
                    max_steps=capture_plan.max_scroll_steps,
                    delay_ms=capture_plan.scroll_step_delay_ms,
                )
                if timings is not None:
                    timings["scroll_ms"] = _elapsed_ms(scroll_start)
                if settle_timeout_ms < 200:
                    if timings is not None:
                        idle_start = time.monotonic()
                        time.sleep(0.2)
                        timings["post_scroll_wait_ms"] = _elapsed_ms(idle_start)
                    else:
                        time.sleep(0.2)
                elif timings is not None:
                    timings["post_scroll_wait_ms"] = 0.0
            elif timings is not None:
                timings["scroll_ms"] = 0.0
                timings["post_scroll_wait_ms"] = 0.0
            settle = settle_timeout_ms / 1000.0
            if settle:
                settle_start = time.monotonic()
                time.sleep(settle)
                if timings is not None:
                    timings["settle_ms"] = _elapsed_ms(settle_start)
            elif timings is not None:
                timings["settle_ms"] = 0.0
            title = driver.title or None
            filename = _build_filename(page_index, title, url, viewport_name)
            screenshot_path = screenshot_dir / filename
            screenshot_start = time.monotonic()
            if capture_plan.full_page_capture:
                _capture_full_page(driver, spec, screenshot_path)
                scroll_height = scroll_height or _evaluate_scroll_height(driver)
            else:
                screenshot_path.write_bytes(driver.get_screenshot_as_png())
            if timings is not None:
                timings["screenshot_ms"] = _elapsed_ms(screenshot_start)
                timings["total_ms"] = _elapsed_ms(attempt_start)
                timing_payload = dict(timings)
            captured += 1
            entry = {
                "index": page_index,
                "url": url,
                "depth": depth,
                "viewport": viewport_name,
                "status": "success",
                "title": title,
                "scroll_height": scroll_height,
                "screenshot_path": str(screenshot_path),
                "error": None,
                "navigation_strategy": None,
                "timeout_seconds": capture_plan.timeout_sec,
                "attempts": 1,
                "attempt_timeout_seconds": capture_plan.timeout_sec,
            }
            if timing_payload is not None:
                entry["timings"] = timing_payload
            entries.append(entry)

            if snapshot_path and not snapshot_written:
                try:
                    html_content = driver.page_source
                    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
                    snapshot_path.write_text(html_content, encoding="utf-8")
                    logger.info(
                        "Wrote fallback HTML snapshot for job_id %s -> %s", job_id, snapshot_path
                    )
                    snapshot_written = True
                except Exception:  # pragma: no cover - disk errors
                    logger.exception("Failed to write fallback HTML snapshot for job_id %s", job_id)

            if is_primary:
                new_links = _collect_links(
                    driver=driver,
                    current_url=url,
                    origin=origin,
                    depth=depth,
                    max_depth=capture_plan.depth,
                    max_pages=capture_plan.max_pages,
                )
        except TimeoutException as exc:
            message = f"timeout: {exc}"
            logger.warning(
                "Selenium timeout for job_id %s (%s) viewport %s: %s",
                job_id,
                safe_url,
                viewport_name,
                exc,
            )
            entry = _failed_entry(
                page_index,
                depth,
                viewport_name,
                url,
                capture_plan.timeout_sec,
                message,
            )
            entries.append(entry)
            failed += 1
            error_messages.append(
                make_error(
                    "timeout",
                    message,
                    retryable=True,
                    details={"url": url, "viewport": viewport_name},
                )
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception(
                "Unexpected Selenium failure for job_id %s (%s) viewport %s",
                job_id,
                safe_url,
                viewport_name,
            )
            entry = _failed_entry(
                page_index,
                depth,
                viewport_name,
                url,
                capture_plan.timeout_sec,
                str(exc),
            )
            entries.append(entry)
            failed += 1
            error_messages.append(
                make_error("runtime", str(exc), details={"url": url, "viewport": viewport_name})
            )
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:  # pragma: no cover - defensive
                    logger.debug("Failed to quit Selenium driver cleanly", exc_info=True)
            if temp_profile is not None:
                temp_profile.cleanup()

    return _CaptureOutcome(entries, captured, failed, error_messages, new_links, snapshot_written)


def _create_driver(
    *,
    webdriver: Any,
    Options: type[Any],
    WebDriverException: type[BaseException],
    viewport_spec: dict[str, Any],
    browser_plan: BrowserPlan,
    runner_plan: RunnerPlan,
) -> tuple[Any, tempfile.TemporaryDirectory[str]]:
    """Create and configure a Selenium Chrome driver for a viewport."""
    width = int(viewport_spec.get("viewport", {}).get("width", 1440))
    height = int(viewport_spec.get("viewport", {}).get("height", 900))
    device_scale = float(viewport_spec.get("device_scale_factor", 1.0))

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument(f"--window-size={width},{height}")

    if browser_plan.user_agent:
        chrome_options.add_argument(f"--user-agent={browser_plan.user_agent}")
    if browser_plan.allow_autoplay:
        chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")

    extra_args = runner_plan.extra.get("chrome_args")
    if isinstance(extra_args, Iterable) and not isinstance(extra_args, str | bytes | bytearray):
        for arg in extra_args:
            chrome_options.add_argument(str(arg))

    temp_profile = tempfile.TemporaryDirectory(prefix="selenium-profile-")
    chrome_options.add_argument(f"--user-data-dir={temp_profile.name}")

    binary_path = runner_plan.extra.get("chrome_binary")
    if binary_path:
        chrome_options.binary_location = str(binary_path)

    service_kwargs: dict[str, Any] = {}
    driver_path = runner_plan.extra.get("driver_path")
    if driver_path:
        try:
            from selenium.webdriver.chrome.service import Service
        except ImportError as exc:  # pragma: no cover - optional dep
            raise _SeleniumImportError("selenium webdriver service unavailable") from exc
        service_kwargs["service"] = Service(str(driver_path))

    try:
        driver = webdriver.Chrome(options=chrome_options, **service_kwargs)
    except WebDriverException:
        temp_profile.cleanup()
        raise

    try:
        driver.execute_cdp_cmd(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": width,
                "height": height,
                "deviceScaleFactor": device_scale,
                "mobile": bool(viewport_spec.get("is_mobile", False)),
            },
        )
    except Exception:  # pragma: no cover - defensive (older browsers)
        logger.debug("Failed to set device metrics override via CDP", exc_info=True)

    return driver, temp_profile


def _apply_browser_mutations(
    driver: Any, browser_plan: BrowserPlan, runner_plan: RunnerPlan
) -> None:
    try:
        driver.execute_script(AUTOPLAY_INIT_SCRIPT)
    except Exception:
        logger.debug("Autoplay script injection failed", exc_info=True)

    if browser_plan.mute_media:
        try:
            driver.execute_script(MUTE_MEDIA_INIT_SCRIPT)
        except Exception:
            logger.debug("Mute media script injection failed", exc_info=True)

    if browser_plan.hide_overlays:
        try:
            driver.execute_script(
                "var style=document.createElement('style');"
                "style.setAttribute('data-selenium-hide-overlays','true');"
                "style.textContent=arguments[0];"
                "document.documentElement.appendChild(style);",
                HIDE_OVERLAY_STYLE,
            )
        except Exception:
            logger.debug("Failed to inject overlay CSS", exc_info=True)

    if browser_plan.reduced_motion:
        try:
            driver.execute_script(REDUCED_MOTION_MATCH_MEDIA_SCRIPT)
        except Exception:
            logger.debug("Reduced motion script injection failed", exc_info=True)

    if browser_plan.disable_animations:
        try:
            driver.execute_script(
                "var s=document.createElement('style');"
                "s.setAttribute('data-selenium-disable-animations','true');"
                "s.textContent=arguments[0];"
                "document.documentElement.appendChild(s);",
                DISABLE_ANIMATIONS_STYLE,
            )
        except Exception:
            logger.debug("Failed to inject disable animations CSS", exc_info=True)

    for css in runner_plan.extra_styles:
        try:
            driver.execute_script(
                (
                    "var s=document.createElement('style');"
                    "s.textContent=arguments[0];"
                    "document.documentElement.appendChild(s);"
                ),
                css,
            )
        except Exception:
            logger.debug("Failed to inject custom CSS", exc_info=True)

    for script in runner_plan.extra_init_scripts:
        try:
            driver.execute_script(script)
        except Exception:
            logger.debug("Failed to run custom init script", exc_info=True)


def _scroll_page(
    driver: Any, *, max_steps: int = MAX_SCROLL_STEPS, delay_ms: int = SCROLL_STEP_DELAY_MS
) -> int:
    driver.execute_script("window.scrollTo(0, 0);")
    last_height = _evaluate_scroll_height(driver)
    for _ in range(max_steps):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(delay_ms / 1000.0)
        new_height = _evaluate_scroll_height(driver)
        reached_bottom = driver.execute_script(
            "return window.scrollY + window.innerHeight >= Math.max("
            "document.body.scrollHeight || 0, document.documentElement.scrollHeight || 0) - 2;"
        )
        if reached_bottom and abs(new_height - last_height) < 2:
            break
        last_height = new_height
    return last_height


def _evaluate_scroll_height(driver: Any) -> int:
    return int(
        driver.execute_script(
            "return Math.max(document.body.scrollHeight || 0, "
            "document.documentElement.scrollHeight || 0, window.innerHeight || 0);"
        )
    )


def _capture_full_page(driver: Any, viewport_spec: dict[str, Any], output_path: Path) -> None:
    width = int(viewport_spec.get("viewport", {}).get("width", 1440))
    device_scale = float(viewport_spec.get("device_scale_factor", 1.0))
    full_height = _evaluate_scroll_height(driver)
    try:
        driver.execute_cdp_cmd(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": width,
                "height": full_height,
                "deviceScaleFactor": device_scale,
                "mobile": bool(viewport_spec.get("is_mobile", False)),
            },
        )
        data = driver.execute_cdp_cmd(
            "Page.captureScreenshot",
            {
                "format": "png",
                "captureBeyondViewport": True,
                "fromSurface": True,
            },
        )["data"]
        output_path.write_bytes(base64.b64decode(data))
    except Exception:  # pragma: no cover - fallback path
        logger.debug(
            "CDP full-page capture failed; falling back to viewport screenshot", exc_info=True
        )
        output_path.write_bytes(driver.get_screenshot_as_png())


def _collect_links(
    *,
    driver: Any,
    current_url: str,
    origin: str,
    depth: int,
    max_depth: int,
    max_pages: int,
) -> list[str]:
    """Return same-origin links discovered on the current page up to max depth."""
    if depth >= max_depth:
        return []

    try:
        hrefs = driver.execute_script(
            "return Array.from("
            "document.querySelectorAll('a[href]'), "
            "el => el.getAttribute('href')"
            ");"
        )
    except Exception:
        return []

    visited: list[str] = []
    seen: set[str] = set()
    for raw_href in hrefs or []:
        if not raw_href:
            continue
        resolved = urljoin(current_url, raw_href)
        normalized = _normalize_url(resolved)
        parsed = urlparse(normalized)
        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc != origin:
            continue
        if normalized in seen:
            continue
        visited.append(normalized)
        seen.add(normalized)
        if len(visited) >= max_pages:
            break
    return visited


def _failed_entry(
    index: int,
    depth: int,
    viewport: str,
    url: str,
    timeout_seconds: float,
    error: str,
) -> dict[str, Any]:
    """Build a standard metadata entry for failed viewport captures."""
    return {
        "index": index,
        "url": url,
        "depth": depth,
        "viewport": viewport,
        "status": "failed",
        "title": None,
        "scroll_height": None,
        "screenshot_path": None,
        "error": error,
        "navigation_strategy": None,
        "timeout_seconds": timeout_seconds,
        "attempts": 1,
        "attempt_timeout_seconds": timeout_seconds,
    }


def _normalize_url(url: str) -> str:
    return normalize_url(url)
