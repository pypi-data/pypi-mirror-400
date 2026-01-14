"""Playwright-backed screenshot capture pipeline.

This module is the primary implementation behind the screenshot CLI and
service surface. It sanitises user-supplied options into deterministic
plans, manages Chromium browser lifecycles, captures HTML snapshots and
PNG artifacts in multiple viewports, and streams the resulting metadata
to the configured storage backend. The orchestration emphasises graceful
degradation: optional features such as async uploads or bundled browsers
are auto-detected and only activated when available.

Example:
    >>> import asyncio
    >>> from pathlib import Path
    >>> from screenshot.models import CaptureOptions, ScreenshotOptions
    >>> options = ScreenshotOptions(capture=CaptureOptions(enabled=True))
    >>> result = asyncio.run(
    ...     capture_screenshots_async(
    ...         "demo",
    ...         "https://example.com",
    ...         store_dir=Path("/tmp/screens"),
    ...         partition_date=None,
    ...         options=options,
    ...     )
    ... )
    >>> result.captured >= 0
    True
"""

from __future__ import annotations

import asyncio
import logging
import math
import os
import re
import sys
import tempfile
import time
from collections import deque
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Protocol, cast, runtime_checkable
from urllib.parse import urljoin, urlparse, urlunparse

from infra_core.logging_utils import sanitize_url
from infra_core.retry import AsyncRetryConfig, RetryCallState, retry_state_summary, run_with_retries

from ._models_plans import BrowserPlan, CapturePlan, RunnerPlan, SanitizedPlans
from ._shared.errors import ScreenshotError, make_error
from ._shared.storage import (
    AsyncStorageBackend,
    CloudStorageBackend,
    LocalStorageBackend,
    StorageBackend,
)
from .defaults import DEFAULTS
from .launch_policy import build_chromium_args, normalise_level
from .models import ScreenshotCaptureResult, ScreenshotOptions

logger = logging.getLogger(__name__)


@runtime_checkable
class CancellationToken(Protocol):
    def raise_if_cancelled(self) -> None: ...


DEFAULT_STORAGE = LocalStorageBackend()


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


MAX_CAPTURE_ATTEMPTS = max(1, int(DEFAULTS.playwright_max_capture_attempts))
ENABLE_TIMING = DEFAULTS.enable_timing

_ENABLE_RUNTIME_BROWSER_INSTALL = os.getenv("ENABLE_RUNTIME_PLAYWRIGHT_INSTALL", "0") == "1"
_INSTALL_LOCK_PATH = Path(tempfile.gettempdir()) / "playwright-install.lock"


class BrowserBundleManager:
    """Manage discovery and installation of bundled Playwright browsers.

    Lifecycle:
    - Discover a colocated `playwright-browsers/` folder up the module path.
    - On first use, set `PLAYWRIGHT_BROWSERS_PATH` to the bundled directory
      (if present) and memoize that environment setup.
    - Optionally perform a runtime install (`playwright install chromium`) when
      the browser is missing and `ENABLE_RUNTIME_PLAYWRIGHT_INSTALL=1` is set.
      A process-wide file lock prevents concurrent installers.

    Notes:
    - The manager only mutates `os.environ` once per process. External env
      overrides are honored, but we log when an override is replaced by the
      bundled path to aid debugging.
    - Runtime installations emit telemetry (success/failure + duration).
    """

    def __init__(self) -> None:
        self._bundle_dir = self._discover_bundled_browser_dir()
        self._env_configured = False
        self._install_lock = asyncio.Lock()

    def bundle_dir(self) -> Path | None:
        return self._bundle_dir

    def ensure_env(self) -> None:
        """Ensure PLAYWRIGHT_BROWSERS_PATH points at the bundled directory if present."""
        if self._env_configured or not self._bundle_dir:
            return
        current_browser_path = os.getenv("PLAYWRIGHT_BROWSERS_PATH")
        if current_browser_path and current_browser_path != str(self._bundle_dir):
            logger.debug(
                "Overriding PLAYWRIGHT_BROWSERS_PATH from %s to %s to use bundled browsers",
                current_browser_path,
                self._bundle_dir,
            )
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(self._bundle_dir)
        self._env_configured = True

    async def ensure_runtime_browser(self) -> bool:
        """Install the bundled browser when missing and runtime install is enabled."""
        if not _ENABLE_RUNTIME_BROWSER_INSTALL:
            return False
        self.ensure_env()
        async with self._install_lock:
            start = time.monotonic()
            handle = await asyncio.to_thread(self._acquire_install_file_lock)
            try:
                ok = await self._ensure_playwright_browsers()
                duration = time.monotonic() - start
                if ok:
                    logger.info("Runtime Playwright install succeeded in %.2fs", duration)
                else:
                    logger.warning("Runtime Playwright install failed after %.2fs", duration)
                return ok
            finally:
                await asyncio.to_thread(self._release_install_file_lock, handle)

    def _discover_bundled_browser_dir(self) -> Path | None:
        start = Path(__file__).resolve()
        for ancestor in [start.parent] + list(start.parents):
            candidate = ancestor / "playwright-browsers"
            if candidate.exists():
                return candidate
        return None

    def _acquire_install_file_lock(self) -> IO[str]:
        _INSTALL_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        handle: IO[str] = open(_INSTALL_LOCK_PATH, "w")
        if os.name == "posix":  # pragma: no cover - platform specific
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        elif os.name == "nt":  # pragma: no cover - platform specific
            import msvcrt

            msvcrt_mod = cast(Any, msvcrt)
            msvcrt_mod.locking(handle.fileno(), msvcrt_mod.LK_LOCK, 1)
        return handle

    def _release_install_file_lock(self, handle: IO[str]) -> None:
        try:
            if os.name == "posix":  # pragma: no cover - platform specific
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            elif os.name == "nt":  # pragma: no cover - platform specific
                import msvcrt

                msvcrt_mod = cast(Any, msvcrt)
                msvcrt_mod.locking(handle.fileno(), msvcrt_mod.LK_UNLCK, 1)
        finally:
            handle.close()

    async def _ensure_playwright_browsers(self) -> bool:
        """Install the Chromium browser at runtime if it is missing."""
        env = os.environ.copy()
        install_dir = env.get("PLAYWRIGHT_BROWSERS_PATH")
        bundle_dir = self._bundle_dir
        if not install_dir and bundle_dir:
            install_dir = str(bundle_dir)
            try:
                bundle_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                # Fall back to default Playwright cache if we cannot create the vendored directory.
                install_dir = env.get("PLAYWRIGHT_BROWSERS_PATH", "")
            else:
                env["PLAYWRIGHT_BROWSERS_PATH"] = install_dir

        logger.warning(
            "Playwright browser missing; attempting runtime install to %s",
            install_dir or "(default cache)",
        )
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "playwright",
            "install",
            "chromium",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            logger.error(
                "Failed to install Playwright Chromium. rc=%s stderr=%s",
                process.returncode,
                stderr.decode().strip(),
            )
            return False

        if stdout:
            logger.info("Playwright Chromium install output: %s", stdout.decode().strip())
        if install_dir:
            os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", install_dir)
        return True


BROWSER_MANAGER = BrowserBundleManager()
BROWSER_MANAGER.ensure_env()

KNOWN_VIEWPORTS: dict[str, dict[str, object]] = {
    "desktop": {
        "viewport": {"width": 1440, "height": 900},
        "device_scale_factor": 1.0,
        "is_mobile": False,
        "has_touch": False,
    },
    "desktop_1080p": {
        "viewport": {"width": 1920, "height": 1080},
        "device_scale_factor": 1.0,
        "is_mobile": False,
        "has_touch": False,
    },
    "desktop_1440p": {
        "viewport": {"width": 2560, "height": 1440},
        "device_scale_factor": 1.0,
        "is_mobile": False,
        "has_touch": False,
    },
    "mobile": {
        "viewport": {"width": 390, "height": 844},
        "device_scale_factor": 2.5,
        "is_mobile": True,
        "has_touch": True,
    },
    "tablet": {
        "viewport": {"width": 768, "height": 1024},
        "device_scale_factor": 2.0,
        "is_mobile": True,
        "has_touch": True,
    },
}

if TYPE_CHECKING:  # pragma: no cover - imported only for typing
    pass

_SLUG_RE = re.compile(r"[^a-z0-9]+")
MEDIA_EXTENSION_RE = re.compile(r"\.(?:mp4|webm|m4v|mp3|wav|aac)(?:\?|$)", re.IGNORECASE)


def _coerce_int(value: object | None, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int | float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value.strip()))
        except ValueError:
            return default
    return default


def _coerce_float(value: object | None, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


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
    """Capture rendered screenshots for a site using Playwright.

    Args:
        job_id: Stable identifier that ties output files back to the calling job.
        source_url: Initial URL to navigate to and capture.
        store_dir: Root directory where assets/metadata partitions are written.
        partition_date: Optional YYYY-MM-DD partition inserted into metadata.
        options: Fully populated `ScreenshotOptions` describing capture plans.
        html_snapshot_path: When provided, capture HTML to this path alongside PNGs.
        cancel_token: Cooperative cancellation hook exposing `raise_if_cancelled`.
        storage: Custom storage backend used for writes/uploads; defaults to local.

    Returns:
        `ScreenshotCaptureResult` summarising how many captures succeeded,
        along with metadata pointers and errors suitable for logging.

    Example:
        >>> from pathlib import Path
        >>> from screenshot.models import CaptureOptions, ScreenshotOptions
        >>> opts = ScreenshotOptions(capture=CaptureOptions(enabled=True))
        >>> asyncio.run(
        ...     capture_screenshots_async(
        ...         "demo",
        ...         "https://example.com",
        ...         store_dir=Path("/tmp/screens"),
        ...         partition_date=None,
        ...         options=opts,
        ...     )
        ... )
    """
    job_identifier = job_id

    storage_backend = storage or DEFAULT_STORAGE

    if not options.capture.enabled:
        return ScreenshotCaptureResult(
            requested=0,
            captured=0,
            failed=0,
            metadata_path=None,
            entries=[],
            errors=[],
            job_id=job_identifier,
        )

    try:
        from playwright.async_api import (
            Error as PlaywrightError,
            TimeoutError as PlaywrightTimeoutError,
            async_playwright,
        )
    except Exception as exc:  # pragma: no cover - depends on optional dep
        message = f"playwright unavailable: {exc}"
        logger.warning("Skipping screenshot capture for job_id %s; %s", job_identifier, message)
        return ScreenshotCaptureResult(
            requested=0,
            captured=0,
            failed=0,
            metadata_path=None,
            entries=[],
            errors=[make_error("dependency", message, retryable=False)],
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

    install_attempted = False

    async def _run_capture() -> ScreenshotCaptureResult:
        nonlocal install_attempted
        entries: list[dict[str, object]] = []
        errors: list[ScreenshotError] = []
        captured = 0
        failed = 0
        requested = 0
        timeout_sec = capture_plan.timeout_sec
        max_attempts = capture_plan.max_capture_attempts
        max_total_duration_sec = capture_plan.max_total_duration_sec
        capture_start = time.monotonic()

        def _check_cancel() -> None:
            if cancel_token is not None:
                cancel_token.raise_if_cancelled()

        _check_cancel()
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
                errors=[
                    make_error(
                        "validation", message, retryable=False, details={"url": normalized_start}
                    )
                ],
                job_id=job_identifier,
            )

        origin = parsed_start.netloc
        queue: deque[tuple[str, int]] = deque()
        visited: set[str] = set()
        enqueued: set[str] = set()

        queue.append((normalized_start, 0))
        enqueued.add(normalized_start)

        browser: Any | None = None
        contexts: dict[str, Any] = {}
        page_pool: dict[str, Any] = {}
        upload_tasks: set[asyncio.Task[None]] = set()
        upload_semaphore = asyncio.Semaphore(4)

        async def _drain_uploads() -> None:
            if not upload_tasks:
                return
            pending = list(upload_tasks)
            if not pending:
                return
            upload_tasks.difference_update(pending)
            await asyncio.gather(*pending, return_exceptions=True)

        def _remove_task(task: asyncio.Task[None]) -> None:
            upload_tasks.discard(task)
            try:
                task.result()
            except Exception:  # pragma: no cover - defensive
                logger.exception("Screenshot upload task failed", exc_info=True)

        async def _upload_worker(path: Path, *, current_url: str) -> None:
            async with upload_semaphore:
                upload_start = time.monotonic()
                safe_url = sanitize_url(current_url)
                try:
                    if isinstance(storage_backend, AsyncStorageBackend):
                        await storage_backend.upload_file_async(path)
                    elif isinstance(storage_backend, CloudStorageBackend):
                        await asyncio.to_thread(storage_backend.upload_file, path)
                    else:
                        # Local storage has no upload step
                        pass
                except Exception as exc:  # pragma: no cover - defensive
                    logger.warning(
                        "Storage upload failed for job_id %s (%s) -> %s; continuing locally (%s)",
                        job_identifier,
                        safe_url,
                        path,
                        exc,
                    )
                else:
                    upload_duration = time.monotonic() - upload_start
                    if upload_duration >= 5.0:
                        logger.warning(
                            "Screenshot upload slow job_id=%s url=%s duration=%.2fs",
                            job_identifier,
                            safe_url,
                            upload_duration,
                        )
                    else:
                        logger.debug(
                            "Screenshot upload job_id=%s url=%s duration=%.2fs",
                            job_identifier,
                            safe_url,
                            upload_duration,
                        )

        def _schedule_upload(path: Path, *, current_url: str) -> None:
            task = asyncio.create_task(_upload_worker(path, current_url=current_url))
            upload_tasks.add(task)
            task.add_done_callback(_remove_task)

        async def _ensure_page(viewport_name: str, context: Any) -> Any:
            page = page_pool.get(viewport_name)
            if page is None or page.is_closed():
                page = await context.new_page()
                page.set_default_timeout(5000)
                if browser_plan.reduced_motion:
                    try:
                        await page.emulate_media(reduced_motion="reduce")
                    except Exception:  # pragma: no cover - defensive
                        logger.debug(
                            "Failed to emulate reduced motion for job_id %s",
                            job_identifier,
                            exc_info=True,
                        )
                page_pool[viewport_name] = page
            return page

        async def _reset_page(viewport_name: str) -> None:
            page = page_pool.pop(viewport_name, None)
            if page is None:
                return
            try:
                await page.close()
            except Exception:  # pragma: no cover - defensive
                logger.debug("Failed to close page for viewport %s", viewport_name, exc_info=True)

        try:
            async with async_playwright() as playwright:
                launch_args: dict[str, Any] = {"headless": True}
                launch_extra_args: list[str] = build_chromium_args(browser_plan.compatibility_level)
                if browser_plan.allow_autoplay:
                    launch_extra_args.append("--autoplay-policy=no-user-gesture-required")
                if launch_extra_args:
                    launch_args["args"] = launch_extra_args
                exec_path = runner_plan.playwright_executable_path
                if exec_path:
                    exec_path_obj = Path(exec_path)
                    if exec_path_obj.exists():
                        launch_args["executable_path"] = str(exec_path_obj)
                    else:
                        logger.warning(
                            "Playwright executable path '%s' not found; "
                            "falling back to bundled browser",
                            exec_path,
                        )
                browser = cast(Any, await playwright.chromium.launch(**launch_args))
                contexts = {}
                for name, spec in capture_plan.viewport_specs.items():
                    viewport_cfg = spec.get("viewport")
                    viewport_dict = dict(viewport_cfg) if isinstance(viewport_cfg, dict) else None
                    context = await browser.new_context(
                        viewport=viewport_dict,
                        device_scale_factor=_coerce_float(spec.get("device_scale_factor"), 1.0),
                        is_mobile=bool(spec.get("is_mobile", False)),
                        has_touch=bool(spec.get("has_touch", False)),
                        user_agent=browser_plan.user_agent,
                    )
                    contexts[name] = context
                init_scripts: list[str] = []
                if browser_plan.allow_autoplay:
                    init_scripts.append(AUTOPLAY_INIT_SCRIPT)
                if browser_plan.mute_media:
                    init_scripts.append(MUTE_MEDIA_INIT_SCRIPT)
                if browser_plan.hide_overlays:
                    init_scripts.append(HIDE_OVERLAY_STYLE)
                if browser_plan.reduced_motion:
                    init_scripts.append(REDUCED_MOTION_MATCH_MEDIA_SCRIPT)
                init_scripts.extend(runner_plan.extra_init_scripts)

                async def _media_route_handler(route: Any) -> None:
                    url = route.request.url
                    if MEDIA_EXTENSION_RE.search(url):
                        await route.abort()
                    else:
                        await route.continue_()

                for context in contexts.values():
                    for script in init_scripts:
                        await context.add_init_script(script)
                    if browser_plan.block_media:
                        await context.route("**/*", _media_route_handler)

                primary_viewport = capture_plan.primary_viewport

                page_counter = 0
                viewport_limit = max(1, capture_plan.max_viewport_concurrency)
                viewport_semaphore = asyncio.Semaphore(max(1, min(len(contexts), viewport_limit)))

                while queue and len(visited) < capture_plan.max_pages:
                    elapsed_total = time.monotonic() - capture_start
                    if elapsed_total >= max_total_duration_sec:
                        logger.warning(
                            "Screenshot budget exceeded",
                            extra={
                                "job_id": job_identifier,
                                "elapsed": elapsed_total,
                                "limit": max_total_duration_sec,
                            },
                        )
                        errors.append(
                            make_error(
                                "budget_exceeded",
                                (
                                    f"budget exceeded after {elapsed_total:.1f}s "
                                    f"(budget {max_total_duration_sec:.1f}s)"
                                ),
                                retryable=False,
                            )
                        )
                        queue.clear()
                        break
                    _check_cancel()
                    url, depth = queue.popleft()
                    if url in visited:
                        continue
                    requested += 1
                    visited.add(url)
                    page_index = page_counter
                    page_counter += 1

                    new_links: list[str] = []

                    async def _capture_for_viewport(
                        viewport_name: str, context: Any
                    ) -> dict[str, object]:
                        async with viewport_semaphore:
                            safe_url = sanitize_url(url)
                            is_primary = viewport_name == primary_viewport
                            title: str | None = None
                            scroll_height: int | None = None
                            timing_payload: dict[str, float] | None = None
                            error_message: str | None = None
                            screenshot_path: Path | None = None
                            status = "failed"
                            strategy_used: str | None = None
                            last_strategy: str | None = None
                            captured_attempt = False
                            attempt_timeout = timeout_sec
                            links_for_viewport: list[str] = []
                            attempt = 0

                            for attempt in range(1, max_attempts + 1):
                                attempt_timeout = timeout_sec * (1.0 + 0.2 * (attempt - 1))
                                recreate_page = False
                                timing_payload = None
                                try:
                                    page = await _ensure_page(viewport_name, context)
                                    _check_cancel()

                                    async def _capture_once() -> None:
                                        nonlocal \
                                            title, \
                                            scroll_height, \
                                            screenshot_path, \
                                            status, \
                                            strategy_used, \
                                            last_strategy, \
                                            links_for_viewport, \
                                            captured_attempt, \
                                            timing_payload
                                        navigation_strategies = runner_plan.navigation_strategies
                                        strategy_used = None
                                        last_strategy = None
                                        timings: dict[str, float] | None = (
                                            {} if ENABLE_TIMING else None
                                        )
                                        attempt_start = time.monotonic()

                                        def _elapsed_ms(start: float) -> float:
                                            return round((time.monotonic() - start) * 1000.0, 3)

                                        async def _navigate_once() -> None:
                                            nonlocal strategy_used, last_strategy
                                            last_err: Exception | None = None
                                            for strategy in navigation_strategies:
                                                strategy_name = strategy.get("name")
                                                last_strategy = (
                                                    str(strategy_name) if strategy_name else None
                                                )
                                                _check_cancel()
                                                wait_until_value = strategy.get(
                                                    "wait_until", "load"
                                                )
                                                wait_until = (
                                                    str(wait_until_value)
                                                    if isinstance(wait_until_value, str)
                                                    else "load"
                                                )
                                                timeout_ms = _coerce_float(
                                                    strategy.get("timeout_ms"),
                                                    timeout_sec * 1000,
                                                )
                                                post_wait = _coerce_float(
                                                    strategy.get("post_wait_ms"), 0.0
                                                )
                                                try:
                                                    await page.goto(
                                                        url,
                                                        wait_until=wait_until,
                                                        timeout=timeout_ms,
                                                    )
                                                    if post_wait:
                                                        wait_start = time.monotonic()
                                                        await page.wait_for_timeout(post_wait)
                                                        if timings is not None:
                                                            timings["post_nav_wait_ms"] = (
                                                                timings.get("post_nav_wait_ms", 0.0)
                                                                + _elapsed_ms(wait_start)
                                                            )
                                                except PlaywrightTimeoutError as exc:
                                                    last_err = exc
                                                    continue
                                                else:
                                                    strategy_used = last_strategy
                                                    return
                                            if last_err is not None:
                                                raise last_err
                                            raise PlaywrightTimeoutError(
                                                "navigation failed without explicit error"
                                            )

                                        def _should_retry(exc: BaseException) -> bool:
                                            # Retry on typical transient navigation issues/timeouts
                                            msg = str(exc).lower()
                                            return (
                                                isinstance(exc, PlaywrightTimeoutError)
                                                or "net::err_" in msg
                                                or "navigation" in msg
                                            )

                                        config = AsyncRetryConfig.create(
                                            max_retries=max(0, max_attempts - 1),
                                            backoff=0.5,
                                            max_backoff=min(5.0, float(timeout_sec)),
                                        )

                                        async def _before_sleep(state: RetryCallState) -> None:
                                            exc, wait_time, _ = retry_state_summary(state)
                                            logger.debug(
                                                "Retrying navigation",
                                                extra={
                                                    "job_id": job_identifier,
                                                    "viewport": viewport_name,
                                                    "url": safe_url,
                                                    "wait": wait_time,
                                                    "error": str(exc),
                                                },
                                            )

                                        nav_start = time.monotonic()
                                        await run_with_retries(
                                            operation=_navigate_once,
                                            config=config,
                                            should_retry=_should_retry,
                                            before_sleep=_before_sleep,
                                        )
                                        if timings is not None:
                                            timings["navigation_ms"] = _elapsed_ms(nav_start)

                                        settle_timeout_ms = capture_plan.settle_timeout_ms
                                        if capture_plan.scroll_enabled:
                                            scroll_start = time.monotonic()
                                            await _scroll_to_bottom(
                                                page,
                                                max_steps=capture_plan.max_scroll_steps,
                                                delay_ms=capture_plan.scroll_step_delay_ms,
                                            )
                                            scroll_height = await _evaluate_scroll_height(page)
                                            if timings is not None:
                                                timings["scroll_ms"] = _elapsed_ms(scroll_start)
                                        else:
                                            scroll_height = None
                                            if timings is not None:
                                                timings["scroll_ms"] = 0.0
                                        should_post_scroll_wait = (
                                            capture_plan.scroll_enabled and settle_timeout_ms < 200
                                        )
                                        if should_post_scroll_wait:
                                            if timings is not None:
                                                idle_start = time.monotonic()
                                                await page.wait_for_timeout(200)
                                                timings["post_scroll_wait_ms"] = _elapsed_ms(
                                                    idle_start
                                                )
                                            else:
                                                await page.wait_for_timeout(200)
                                        elif timings is not None:
                                            timings["post_scroll_wait_ms"] = 0.0
                                        style_snippets: list[str] = list(runner_plan.extra_styles)
                                        if browser_plan.disable_animations:
                                            style_snippets.insert(0, DISABLE_ANIMATIONS_STYLE)
                                        style_start = time.monotonic()
                                        for style_snippet in style_snippets:
                                            try:
                                                await page.add_style_tag(content=style_snippet)
                                            except Exception:  # pragma: no cover - defensive
                                                logger.debug(
                                                    "Failed to inject style snippet for job_id %s",
                                                    job_identifier,
                                                    exc_info=True,
                                                )
                                        if timings is not None:
                                            timings["style_ms"] = _elapsed_ms(style_start)
                                        if settle_timeout_ms:
                                            settle_start = time.monotonic()
                                            await page.wait_for_timeout(settle_timeout_ms)
                                            if timings is not None:
                                                timings["settle_ms"] = _elapsed_ms(settle_start)
                                        elif timings is not None:
                                            timings["settle_ms"] = 0.0
                                        _check_cancel()
                                        title = await _safe_title(page)
                                        filename = _build_filename(
                                            page_index, title, url, viewport_name
                                        )
                                        path = screenshot_dir / filename

                                        async def _take_screenshot() -> None:
                                            await page.screenshot(
                                                path=str(path),
                                                full_page=capture_plan.full_page_capture,
                                                type="png",
                                                timeout=30000,
                                            )

                                        def _should_retry_ss(exc: BaseException) -> bool:
                                            msg = str(exc).lower()
                                            return (
                                                isinstance(exc, PlaywrightTimeoutError)
                                                or "target closed" in msg
                                                or "protocol error" in msg
                                            )

                                        ss_config = AsyncRetryConfig.create(
                                            max_retries=1, backoff=0.2, max_backoff=1.0
                                        )
                                        screenshot_start = time.monotonic()
                                        await run_with_retries(
                                            operation=_take_screenshot,
                                            config=ss_config,
                                            should_retry=_should_retry_ss,
                                        )
                                        if timings is not None:
                                            timings["screenshot_ms"] = _elapsed_ms(screenshot_start)
                                            timings["total_ms"] = _elapsed_ms(attempt_start)
                                        _schedule_upload(path, current_url=url)
                                        screenshot_path = path
                                        status = "success"
                                        captured_attempt = True
                                        if timings is not None:
                                            timing_payload = dict(timings)
                                        if is_primary:
                                            links_for_viewport = await _extract_links(
                                                page,
                                                current_url=url,
                                                origin=origin,
                                                depth=depth,
                                                max_depth=capture_plan.depth,
                                                visited=visited,
                                                enqueued=enqueued,
                                                max_pages=capture_plan.max_pages,
                                            )

                                        if html_snapshot_path and not html_snapshot_path.exists():
                                            try:
                                                html_content = await page.content()
                                                write_async = getattr(
                                                    storage_backend, "write_text_async", None
                                                )
                                                if write_async is not None:
                                                    write_async_fn = cast(
                                                        Callable[[Path, str], Awaitable[Path]],
                                                        write_async,
                                                    )
                                                    await write_async_fn(
                                                        html_snapshot_path, html_content
                                                    )
                                                else:
                                                    await asyncio.to_thread(
                                                        storage_backend.write_text,
                                                        html_snapshot_path,
                                                        html_content,
                                                    )
                                                logger.info(
                                                    "Wrote fallback HTML snapshot for job_id %s "
                                                    "-> %s",
                                                    job_identifier,
                                                    html_snapshot_path,
                                                )
                                            except Exception:  # pragma: no cover - defensive
                                                logger.exception(
                                                    "Failed to write fallback HTML snapshot "
                                                    "for job_id %s",
                                                    job_identifier,
                                                )

                                    await asyncio.wait_for(_capture_once(), timeout=attempt_timeout)
                                    error_message = None
                                    break
                                except TimeoutError:
                                    error_message = (
                                        f"capture timeout after {attempt_timeout:.1f}s "
                                        f"(attempt {attempt}/{max_attempts})"
                                    )
                                    logger.warning(
                                        "Screenshot capture timeout for job_id %s (%s) "
                                        "attempt %d/%d",
                                        job_identifier,
                                        url,
                                        attempt,
                                        max_attempts,
                                    )
                                    recreate_page = True
                                except PlaywrightTimeoutError as exc:
                                    error_message = (
                                        f"timeout: {exc} (attempt {attempt}/{max_attempts})"
                                    )
                                    logger.warning(
                                        "Screenshot navigation timeout for job_id %s (%s) "
                                        "attempt %d/%d: %s",
                                        job_identifier,
                                        url,
                                        attempt,
                                        max_attempts,
                                        exc,
                                    )
                                    recreate_page = True
                                except Exception as exc:  # pragma: no cover - defensive
                                    error_message = str(exc)
                                    logger.exception(
                                        "Failed to capture screenshot for job_id %s (%s) "
                                        "attempt %d/%d",
                                        job_identifier,
                                        url,
                                        attempt,
                                        max_attempts,
                                    )
                                    recreate_page = True
                                finally:
                                    if recreate_page:
                                        await _reset_page(viewport_name)

                                if error_message and attempt < max_attempts:
                                    _check_cancel()
                                    await asyncio.sleep(0.5)

                            entry = {
                                "index": page_index,
                                "url": url,
                                "depth": depth,
                                "viewport": viewport_name,
                                "status": status,
                                "title": title,
                                "scroll_height": scroll_height,
                                "screenshot_path": str(screenshot_path)
                                if screenshot_path
                                else None,
                                "error": error_message if not captured_attempt else None,
                                "navigation_strategy": strategy_used or last_strategy,
                                "timeout_seconds": timeout_sec,
                                "attempts": attempt,
                                "attempt_timeout_seconds": attempt_timeout,
                            }
                            if timing_payload is not None:
                                entry["timings"] = timing_payload
                            logger.debug(
                                "Screenshot entry job_id=%s viewport=%s url=%s status=%s "
                                "attempts=%d error=%s",
                                job_identifier,
                                viewport_name,
                                safe_url,
                                status,
                                attempt,
                                (error_message if error_message and not captured_attempt else None),
                            )

                            return {
                                "entry": entry,
                                "captured": 1 if status == "success" else 0,
                                "failed": 0 if status == "success" else 1,
                                "new_links": links_for_viewport
                                if status == "success" and is_primary
                                else [],
                            }

                    viewport_results = await asyncio.gather(
                        *(
                            _capture_for_viewport(viewport_name, context)
                            for viewport_name, context in contexts.items()
                        )
                    )

                    for result in viewport_results:
                        entry_payload = cast(dict[str, object], result["entry"])
                        entries.append(entry_payload)
                        captured += cast(int, result["captured"])
                        failed += cast(int, result["failed"])
                        new_links_candidate = cast(list[str], result.get("new_links", []))
                        if new_links_candidate:
                            new_links = new_links_candidate

                    if new_links:
                        remaining_capacity = max(
                            0,
                            capture_plan.max_pages - len(visited) - len(queue),
                        )
                        for link in new_links:
                            if remaining_capacity <= 0:
                                break
                            _check_cancel()
                            queue.append((link, depth + 1))
                            enqueued.add(link)
                            remaining_capacity -= 1

                await _drain_uploads()
                await asyncio.gather(
                    *(page.close() for page in page_pool.values() if not page.is_closed()),
                    return_exceptions=True,
                )
                page_pool.clear()
                await asyncio.gather(*(context.close() for context in contexts.values()))
                await browser.close()
        except (TimeoutError, asyncio.CancelledError):
            # Timeout or cancellation - force cleanup of browser resources
            logger.warning(
                "Screenshot capture cancelled/timeout for job_id %s - cleaning up browser",
                job_identifier,
            )
            try:
                await _drain_uploads()
            except Exception:  # pragma: no cover - defensive
                pass
            try:
                if page_pool:
                    await asyncio.gather(
                        *(page.close() for page in page_pool.values() if not page.is_closed()),
                        return_exceptions=True,
                    )
                    page_pool.clear()
            except Exception:  # pragma: no cover - defensive
                pass
            try:
                if contexts:
                    await asyncio.gather(
                        *(context.close() for context in contexts.values()), return_exceptions=True
                    )
                if browser:
                    await browser.close()
            except Exception:  # pragma: no cover
                pass
            raise  # Re-raise to propagate cancellation/timeout
        except Exception as exc:  # pragma: no cover - defensive
            try:
                await _drain_uploads()
            except Exception:  # pragma: no cover - defensive
                pass
            try:
                if page_pool:
                    await asyncio.gather(
                        *(page.close() for page in page_pool.values() if not page.is_closed()),
                        return_exceptions=True,
                    )
                    page_pool.clear()
            except Exception:  # pragma: no cover - defensive
                pass
            try:
                if contexts:
                    await asyncio.gather(
                        *(context.close() for context in contexts.values()), return_exceptions=True
                    )
                if browser:
                    await browser.close()
            except Exception:  # pragma: no cover - defensive
                pass
            if (
                _ENABLE_RUNTIME_BROWSER_INSTALL
                and not install_attempted
                and _is_missing_playwright_browser(exc)
            ):
                install_attempted = True
                if await BROWSER_MANAGER.ensure_runtime_browser():
                    return await _run_capture()
            elif _is_missing_playwright_browser(exc):
                logger.error(
                    "Playwright browser missing but runtime install is disabled; "
                    "set ENABLE_RUNTIME_PLAYWRIGHT_INSTALL=1 to allow automatic download."
                )
            if isinstance(exc, PlaywrightError):
                logger.exception(
                    "Playwright failure during screenshot capture for job_id %s", job_identifier
                )
            else:
                logger.exception(
                    "Unexpected failure during screenshot capture for job_id %s", job_identifier
                )
            message = f"playwright session failed: {exc}"
            errors.append(
                make_error(
                    "playwright_runtime",
                    message,
                    retryable=_is_missing_playwright_browser(exc),
                    details={"job_id": job_identifier},
                )
            )

        metadata: dict[str, object] = {
            "schema_version": "screenshot_capture/v1",
            "job_id": job_identifier,
            "source_url": source_url,
            "fetched_at": utc_now_iso(),
            "options": {
                "max_pages": capture_plan.max_pages,
                "depth": capture_plan.depth,
                "delay_ms": capture_plan.delay_ms,
                "viewports": list(capture_plan.viewport_details),
                "navigation_strategies": [
                    dict(strategy) for strategy in runner_plan.navigation_strategies
                ],
                "timeout_sec": capture_plan.timeout_sec,
                "max_viewport_concurrency": capture_plan.max_viewport_concurrency,
                "scroll_step_delay_ms": capture_plan.scroll_step_delay_ms,
                "max_scroll_steps": capture_plan.max_scroll_steps,
            },
            "entries": entries,
            "errors": [error.to_dict() for error in errors],
        }
        metadata_path = metadata_dir / "screenshots.json"
        write_json_async = getattr(storage_backend, "write_json_async", None)
        if write_json_async is not None:
            write_json_fn = cast(
                Callable[[Path, dict[str, object]], Awaitable[Path]],
                write_json_async,
            )
            metadata_path = await write_json_fn(metadata_path, metadata)
        else:
            metadata_path = await asyncio.to_thread(
                storage_backend.write_json, metadata_path, metadata
            )

        return ScreenshotCaptureResult(
            requested=requested,
            captured=captured,
            failed=failed,
            metadata_path=metadata_path,
            entries=entries,
            errors=errors,
            job_id=job_identifier,
        )

    # Proper async implementation: Use asyncio.timeout for cancellable timeouts.
    # This allows tasks to be properly cancelled when timeout occurs,
    # preventing thread leaks and zombie browser processes.
    max_duration = capture_plan.max_total_duration_sec or 300.0
    # Add 20% buffer for browser startup, page transitions, etc.
    max_duration_with_buffer = max_duration * 1.2

    try:
        async with asyncio.timeout(max_duration_with_buffer):
            return await _run_capture()
    except TimeoutError:
        logger.error(
            "Screenshot capture timed out for job_id %s after %.1fs "
            "(calculated max: %.1fs + 20%% buffer)",
            job_identifier,
            max_duration_with_buffer,
            max_duration,
        )
        return ScreenshotCaptureResult(
            requested=0,
            captured=0,
            failed=1,
            metadata_path=None,
            entries=[],
            errors=[
                make_error(
                    "timeout",
                    f"capture timed out after {max_duration_with_buffer:.1f}s",
                    retryable=True,
                )
            ],
            job_id=job_identifier,
        )


def capture_screenshots(
    job_id: str,
    source_url: str,
    *,
    store_dir: Path,
    partition_date: str | None,
    options: ScreenshotOptions,
    html_snapshot_path: Path | None = None,
    cancel_token: CancellationToken | None = None,
) -> ScreenshotCaptureResult:
    """Capture rendered screenshots synchronously for convenience.

    Args:
        job_id: Stable identifier that maps outputs back to the caller.
        source_url: URL entry point to load and capture.
        store_dir: Directory where per-job folders should be created.
        partition_date: Optional YYYY-MM-DD partition used in metadata.
        options: Screenshot configuration shared with the async variant.
        html_snapshot_path: Optional path that receives the HTML archive.
        cancel_token: Optional cooperative cancellation hook.

    Returns:
        `ScreenshotCaptureResult` produced by `capture_screenshots_async`.

    Example (synchronous helper shown for completeness):
        >>> from pathlib import Path
        >>> from screenshot.models import CaptureOptions, ScreenshotOptions
        >>> result = capture_screenshots(
        ...     "demo",
        ...     "https://example.com",
        ...     store_dir=Path("/tmp/screens"),
        ...     partition_date=None,
        ...     options=ScreenshotOptions(capture=CaptureOptions(enabled=True)),
        ... )
        >>> result.job_id
        'demo'

    Note:
        This helper spins up a dedicated event loop via `asyncio.run`, so it
        should only be used from synchronous entry points such as CLIs.
        Async code should call `capture_screenshots_async` directly.
    """
    return asyncio.run(
        capture_screenshots_async(
            job_id,
            source_url,
            store_dir=store_dir,
            partition_date=partition_date,
            options=options,
            html_snapshot_path=html_snapshot_path,
            cancel_token=cancel_token,
        )
    )


def _is_missing_playwright_browser(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "executable doesn't exist at" in message
        or "browser needs to be installed" in message
        or "playwright install" in message
    )


def _sanitize_options(options: ScreenshotOptions) -> SanitizedPlans:
    capture = options.capture
    browser = options.browser
    runner = options.runner

    max_pages = max(1, int(capture.max_pages))
    depth = max(0, int(capture.depth))
    delay_ms = max(0, int(math.ceil(capture.post_nav_wait_s * 1000)))
    # Use 5.0 second minimum timeout to ensure adequate time for real-world page loads.
    # Even fast pages may need DNS resolution, TLS handshake, and initial render time.
    timeout_sec = max(5.0, float(capture.timeout_s))
    max_attempts = max(1, int(capture.max_capture_attempts or MAX_CAPTURE_ATTEMPTS))
    max_viewport_concurrency = max(1, int(capture.max_viewport_concurrency))
    scroll_step_delay_ms = max(0, int(capture.scroll_step_delay_ms))
    max_scroll_steps = max(0, int(capture.max_scroll_steps))

    viewports = list(capture.viewports) or ["desktop"]
    viewport_specs: dict[str, dict[str, object]] = {}
    viewport_details: list[dict[str, object]] = []

    def _build_viewport_detail(name: str, preset: dict[str, object]) -> dict[str, object]:
        viewport_cfg = preset.get("viewport")
        width = height = 0
        if isinstance(viewport_cfg, dict):
            width = _coerce_int(viewport_cfg.get("width"), 0)
            height = _coerce_int(viewport_cfg.get("height"), 0)
        return {
            "name": name,
            "width": width,
            "height": height,
            "device_scale_factor": _coerce_float(preset.get("device_scale_factor"), 1.0),
            "is_mobile": bool(preset.get("is_mobile", False)),
        }

    for viewport in viewports:
        if isinstance(viewport, str):
            preset = KNOWN_VIEWPORTS.get(viewport)
            if not preset:
                logger.warning("Unknown viewport preset '%s'; skipping", viewport)
                continue
            viewport_specs[viewport] = preset
            viewport_details.append(_build_viewport_detail(viewport, preset))

    if not viewport_specs:
        fallback = KNOWN_VIEWPORTS["desktop"]
        viewport_specs["desktop"] = fallback
        viewport_details.append(_build_viewport_detail("desktop", fallback))

    primary_viewport = next(iter(viewport_specs.keys()))
    navigation_strategies = [
        {
            "name": "networkidle_10s",
            "wait_until": "networkidle",
            "timeout_ms": 10_000,
            "post_wait_ms": delay_ms,  # honor the user’s delay
        },
        {
            "name": "domcontentloaded_6s",
            "wait_until": "domcontentloaded",
            "timeout_ms": 6_000,
            "post_wait_ms": max(delay_ms, 1_000),  # brief settle time even if delay=0
        },
        {
            "name": "load_wait_4s",
            "wait_until": "load",
            "timeout_ms": 4_000,
            "post_wait_ms": max(delay_ms, 2_000),  # longer tail for late assets
        },
    ]

    if capture.max_total_duration_s:
        max_total_duration_sec = float(capture.max_total_duration_s)
    else:
        max_total_duration_sec = timeout_sec * max_pages * max(1, len(viewports))

    settle_timeout_ms = max(0, int(round((capture.pre_capture_wait_s or 0) * 1000)))

    extra_styles = list(runner.extra_styles)
    extra_init_scripts = list(runner.extra_init_scripts)
    forgiveness_level = normalise_level(browser.compatibility_level)
    override_user_agent = browser.user_agent

    capture_plan = CapturePlan(
        max_pages=max_pages,
        depth=depth,
        delay_ms=delay_ms,
        viewport_specs=viewport_specs,
        viewport_details=viewport_details,
        primary_viewport=primary_viewport,
        timeout_sec=timeout_sec,
        max_total_duration_sec=max_total_duration_sec,
        max_capture_attempts=max_attempts,
        max_viewport_concurrency=max_viewport_concurrency,
        scroll_enabled=bool(capture.scroll),
        scroll_step_delay_ms=scroll_step_delay_ms,
        max_scroll_steps=max_scroll_steps,
        full_page_capture=bool(capture.full_page),
        settle_timeout_ms=settle_timeout_ms,
    )

    browser_plan = BrowserPlan(
        allow_autoplay=bool(browser.allow_autoplay),
        hide_overlays=bool(browser.hide_overlays),
        reduced_motion=bool(browser.reduced_motion),
        disable_animations=bool(browser.disable_animations),
        mute_media=bool(browser.mute_media),
        block_media=bool(browser.block_media),
        compatibility_level=forgiveness_level,
        user_agent=override_user_agent,
    )

    runner_plan = RunnerPlan(
        extra_styles=tuple(extra_styles),
        extra_init_scripts=tuple(extra_init_scripts),
        navigation_strategies=tuple(navigation_strategies),
        playwright_executable_path=runner.playwright_executable_path,
        extra=dict(runner.extra),
    )

    return SanitizedPlans(capture=capture_plan, browser=browser_plan, runner=runner_plan)


async def _scroll_to_bottom(page: Any, *, max_steps: int, delay_ms: int) -> None:
    # page.set_default_timeout() already set to 5s, applies to all evaluate() calls
    await page.evaluate("window.scrollTo(0, 0)")
    last_height = await _evaluate_scroll_height(page)
    for _ in range(max_steps):
        await page.evaluate("window.scrollBy(0, window.innerHeight)")
        await page.wait_for_timeout(delay_ms)
        new_height = await _evaluate_scroll_height(page)
        reached_bottom = await page.evaluate(
            """
            window.scrollY + window.innerHeight >=
            Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight,
            ) - 2
            """
        )
        if reached_bottom and abs(new_height - last_height) < 2:
            break
        last_height = new_height


async def _evaluate_scroll_height(page: Any) -> int:
    height = await page.evaluate(
        """
        Math.max(
            document.body.scrollHeight || 0,
            document.documentElement.scrollHeight || 0,
            window.innerHeight || 0,
        )
        """
    )
    return int(height or 0)


async def _safe_title(page: Any) -> str | None:
    try:
        title = await page.title()
    except Exception:  # pragma: no cover - keep capture resilient
        return None
    return title or None


async def _extract_links(
    page: Any,
    *,
    current_url: str,
    origin: str,
    depth: int,
    max_depth: int,
    visited: set[str],
    enqueued: set[str],
    max_pages: int,
) -> list[str]:
    if depth >= max_depth:
        return []

    try:
        hrefs = await page.eval_on_selector_all(
            "a[href]", "elements => elements.map(el => el.getAttribute('href'))"
        )
    except Exception:  # pragma: no cover - keep capture resilient
        return []

    results: list[str] = []
    for raw_href in hrefs:
        if not raw_href:
            continue
        resolved = urljoin(current_url, raw_href)
        normalized = _normalize_url(resolved)
        parsed = urlparse(normalized)
        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc != origin:
            continue
        if normalized in visited or normalized in enqueued:
            continue
        results.append(normalized)
        enqueued.add(normalized)
        if len(results) + len(visited) >= max_pages:
            break

    return results


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    normalized = parsed._replace(fragment="")
    if normalized.path.endswith("/") and normalized.path != "/":
        normalized = normalized._replace(path=normalized.path.rstrip("/"))
    return urlunparse(normalized)


def _build_filename(index: int, title: str | None, url: str, viewport: str) -> str:
    label = title or urlparse(url).path.rsplit("/", 1)[-1] or url
    label = label.strip().lower()
    label = _SLUG_RE.sub("-", label)
    label = label.strip("-") or "page"
    return f"{index:03d}-{label}-{viewport}.png"


AUTOPLAY_INIT_SCRIPT = """
(() => {
  const enableAutoplay = () => {
    const mediaElements = Array.from(document.querySelectorAll('video, audio'));
    for (const media of mediaElements) {
      try {
        media.muted = true;
        media.autoplay = true;
        media.playsInline = true;
        media.setAttribute('muted', '');
        media.setAttribute('autoplay', '');
        media.setAttribute('playsinline', '');
        if (typeof media.play === 'function') {
          media.play().catch(() => {});
        }
      } catch (err) {
        // ignore
      }
    }
  };
  enableAutoplay();
  document.addEventListener('DOMContentLoaded', enableAutoplay, { once: false });
})();
"""

MUTE_MEDIA_INIT_SCRIPT = """
(() => {
  const forceMuted = () => {
    try {
      const descriptor = Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype, 'muted');
      if (descriptor && descriptor.configurable) {
        Object.defineProperty(HTMLMediaElement.prototype, 'muted', {
          configurable: true,
          enumerable: descriptor.enumerable,
          get() { return true; },
          set() { /* noop */ },
        });
      }
    } catch (err) {
      // noop
    }
  };
  forceMuted();
  document.addEventListener('DOMContentLoaded', forceMuted, { once: false });
})();
"""

REDUCED_MOTION_MATCH_MEDIA_SCRIPT = """
(() => {
  const originalMatchMedia = window.matchMedia;
  window.matchMedia = (query) => {
    if (typeof query === 'string' && query.includes('prefers-reduced-motion')) {
      return {
        matches: true,
        media: query,
        addListener() {},
        removeListener() {},
        addEventListener() {},
        removeEventListener() {},
        onchange: null,
      };
    }
    return originalMatchMedia.call(window, query);
  };
})();
"""

DISABLE_ANIMATIONS_STYLE = """
*,
*::before,
*::after {
  animation-duration: 0.001s !important;
  animation-iteration-count: 1 !important;
  transition-duration: 0.001s !important;
  transition-delay: 0s !important;
  scroll-behavior: auto !important;
}
"""

HIDE_OVERLAY_STYLE = """
(() => {
  const style = document.createElement('style');
  style.setAttribute('data-screenshot-hide-overlays', 'true');
  style.textContent = `
    [aria-label*="autoplay" i],
    [aria-label*="allow autoplay" i],
    [role="dialog"][aria-label*="autoplay" i],
    [role="dialog"][aria-label*="cookie" i],
    .cookie-banner,
    .cookie,
    .cookies,
    .consent,
    .gdpr,
    .gdpr-wrapper,
    .eu-cookie,
    .cmp-overlay,
    .cmp-container,
    .banner,
    .modal,
    .modal-consent,
    .overlay,
    .notification,
    .toast {
      display: none !important;
      visibility: hidden !important;
    }
  `;
  const apply = () => {
    if (!document.head) {
      return;
    }
    if (!document.head.querySelector('[data-screenshot-hide-overlays]')) {
      document.head.appendChild(style.cloneNode(true));
    }
  };
  apply();
  document.addEventListener('DOMContentLoaded', apply, { once: false });
})();
"""
