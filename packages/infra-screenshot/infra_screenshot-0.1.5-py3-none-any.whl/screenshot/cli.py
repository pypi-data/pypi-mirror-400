"""Standalone CLI for running screenshot jobs locally with multiple backends.

The CLI primarily targets local development workflows where engineers want to
verify how Playwright or Selenium backends behave without deploying the full
service stack. It translates CLI arguments into `ScreenshotJob` payloads and
streams them through the shared `ScreenshotService`.

Example:
    $ python -m screenshot.cli local --urls https://example.com --output-dir ./out
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from collections.abc import Iterable
from pathlib import Path

from . import (
    ScreenshotBackend,
    ScreenshotCaptureResult,
    ScreenshotJob as GenericScreenshotJob,
    ScreenshotService,
)
from ._shared.storage import LocalStorageBackend, StorageBackend
from .cli_shared import add_job_arguments, build_cli_args
from .cli_utils import collect_job_specs
from .playwright_runner import capture_screenshots_async as playwright_capture_async
from .selenium_runner import capture_screenshots_async as selenium_capture_async

logger = logging.getLogger("screenshot.cli")

GLOBAL_FLAG_ENV = "SCREENSHOT_CLI_USE_CONFIG"
CONFIG_PATH_ENV = "SCREENSHOT_CLI_CONFIG_PATH"


def _env_truthy(value: str | None, *, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _cli_config_enabled() -> bool:
    enabled = _env_truthy(os.getenv(GLOBAL_FLAG_ENV), default=True)
    logger.debug(
        "Using %s arguments for screenshot local CLI",
        "config preset=local_execution" if enabled else "programmatic",
    )
    return enabled


def _cli_config_path() -> Path | None:
    raw = os.getenv(CONFIG_PATH_ENV)
    return Path(raw) if raw else None


class PlaywrightScreenshotBackend(ScreenshotBackend[ScreenshotCaptureResult]):
    """Screenshot backend that uses the bundled Playwright runner."""

    def __init__(self, *, storage: StorageBackend | None = None) -> None:
        self._storage = storage or LocalStorageBackend()

    async def run_job_async(self, job: GenericScreenshotJob) -> ScreenshotCaptureResult:
        result = await playwright_capture_async(
            job.job_id,
            job.url,
            store_dir=job.output_root,
            partition_date=job.partition_date,
            options=job.options,
            html_snapshot_path=job.html_snapshot_path,
            cancel_token=job.cancel_token,
            storage=self._storage,
        )
        if result.job_id is None:
            result.job_id = job.job_id
        return result


class SeleniumScreenshotBackend(ScreenshotBackend[ScreenshotCaptureResult]):
    """Screenshot backend powered by Selenium + Chromium."""

    def __init__(self, *, storage: StorageBackend | None = None) -> None:
        self._storage = storage or LocalStorageBackend()

    async def run_job_async(self, job: GenericScreenshotJob) -> ScreenshotCaptureResult:
        result = await selenium_capture_async(
            job.job_id,
            job.url,
            store_dir=job.output_root,
            partition_date=job.partition_date,
            options=job.options,
            html_snapshot_path=job.html_snapshot_path,
            cancel_token=job.cancel_token,
            storage=self._storage,
        )
        if result.job_id is None:
            result.job_id = job.job_id
        return result


def build_local_screenshot_service(
    *,
    concurrency: int = 1,
    storage: StorageBackend | None = None,
    backend: str = "playwright",
) -> ScreenshotService[ScreenshotCaptureResult]:
    """Return a ScreenshotService backed by the requested engine.

    Args:
        concurrency: Number of jobs to run concurrently (minimum 1).
        storage: Optional storage backend override for screenshot artifacts.
        backend: Runner choice; either "playwright" or "selenium".

    Returns:
        Configured `ScreenshotService` ready to execute jobs.

    Example:
        >>> service = build_local_screenshot_service(concurrency=2, backend="playwright")
        >>> isinstance(service, ScreenshotService)
        True
    """

    backend_name = (backend or "playwright").strip().lower()
    backend_impl: ScreenshotBackend[ScreenshotCaptureResult]
    if backend_name == "selenium":
        backend_impl = SeleniumScreenshotBackend(storage=storage)
    elif backend_name == "playwright":
        backend_impl = PlaywrightScreenshotBackend(storage=storage)
    else:
        raise ValueError(f"Unsupported backend '{backend}'")
    return ScreenshotService(backend_impl, concurrency=max(1, concurrency))


def _configure_logging(verbose: bool) -> None:
    """Configure the CLI logger according to the verbosity flag."""

    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format="%(message)s")


def build_parser() -> argparse.ArgumentParser:
    """Return the top-level argparse parser for the screenshot CLI."""

    parser = argparse.ArgumentParser(description="Generic screenshot capture utilities")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    subparsers = parser.add_subparsers(dest="command", required=True)

    local_parser = subparsers.add_parser("local", help="Capture screenshots locally")
    use_config = _cli_config_enabled()
    add_job_arguments(
        local_parser,
        include_output_dir=True,
        use_config=use_config,
        config_path=_cli_config_path() if use_config else None,
        preset="local_execution" if use_config else None,
    )
    local_parser.add_argument(
        "--site-concurrency",
        dest="site_concurrency",
        type=int,
        default=1,
        help="Number of sites to capture in parallel",
    )
    local_parser.add_argument(
        "--summary-file",
        type=Path,
        help="Optional path to write JSON summary output",
    )

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    """CLI entry point for executing screenshot capture commands.

    Args:
        argv: Sequence of command-line arguments; defaults to `sys.argv[1:]`.

    Returns:
        Exit status code compatible with `sys.exit`.

    Example:
        >>> args = [\"local\", \"--urls\", \"https://example.com\", \"--output-dir\", \"./out\"]
        >>> main(args)  # doctest: +SKIP
        0
    """

    parser = build_parser()

    args = parser.parse_args(list(argv) if argv is not None else None)
    _configure_logging(args.verbose)

    if args.command == "local":
        return _cmd_local(args)

    parser.error(f"Unknown command: {args.command}")
    return 1


def _cmd_local(args: argparse.Namespace) -> int:
    """Execute local screenshot captures based on parsed CLI arguments."""

    cli_args = build_cli_args(args)
    try:
        specs = collect_job_specs(cli_args)
    except FileNotFoundError:
        if args.input:
            logger.error("Input file %s not found", args.input)
        return 1
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse %s: %s", args.input, exc)
        return 1
    except ValueError as exc:
        logger.error(str(exc))
        return 1

    if logger.isEnabledFor(logging.DEBUG):
        if specs:
            resolved = specs[0]["options"]  # Already typed as ScreenshotOptions
            summary = {
                "backend": specs[0].get("backend", cli_args.backend),
                "enabled": resolved.capture.enabled,
                "max_pages": resolved.capture.max_pages,
                "depth": resolved.capture.depth,
                "viewports": list(resolved.capture.viewports),
                "scroll": resolved.capture.scroll,
                "full_page": resolved.capture.full_page,
                "post_nav_wait_s": resolved.capture.post_nav_wait_s,
                "pre_capture_wait_s": resolved.capture.pre_capture_wait_s,
                "timeout_s": resolved.capture.timeout_s,
                "allow_autoplay": resolved.browser.allow_autoplay,
                "hide_overlays": resolved.browser.hide_overlays,
                "reduced_motion": resolved.browser.reduced_motion,
                "mute_media": resolved.browser.mute_media,
                "disable_animations": resolved.browser.disable_animations,
                "block_media": resolved.browser.block_media,
                "extra_css": len(resolved.runner.extra_styles),
                "extra_js": len(resolved.runner.extra_init_scripts),
            }
            logger.debug("Resolved options: %s", summary)
        else:
            logger.debug("Resolved options: no jobs provided")

    if not specs:
        logger.error("No screenshot jobs specified; provide --urls or --input")
        return 1

    backend_choices = {
        str(spec.get("backend", cli_args.backend or "playwright") or "playwright") for spec in specs
    }
    if len(backend_choices) > 1:
        logger.error(
            "Mixed backend selections are not supported: %s", ", ".join(sorted(backend_choices))
        )
        return 1
    selected_backend = backend_choices.pop()

    output_root: Path = args.output_dir
    output_root.mkdir(parents=True, exist_ok=True)

    jobs: list[GenericScreenshotJob] = []

    for spec in specs:
        job_id = spec["job_id"]
        url = spec["url"]
        options = spec["options"]
        partition_date = spec.get("partition_date")
        meta = spec.get("metadata", {})
        snapshot_raw = spec.get("html_snapshot_path")
        snapshot_path = Path(snapshot_raw) if snapshot_raw else None
        jobs.append(
            GenericScreenshotJob(
                job_id=job_id,
                url=url,
                output_root=output_root,
                options=options,
                partition_date=partition_date,
                html_snapshot_path=snapshot_path,
                metadata=dict(meta),
            )
        )

    try:
        service = build_local_screenshot_service(
            concurrency=max(1, args.site_concurrency),
            backend=selected_backend,
        )
    except ValueError as exc:
        logger.error(str(exc))
        return 1
    batch_result = service.capture(jobs)

    for result in batch_result.results:
        job_label = result.job_id or "unknown"
        if result.succeeded:
            logger.info(
                "Screenshot job %s succeeded (captured %d/%d)",
                job_label,
                result.captured,
                result.requested,
            )
        else:
            error_text = (
                "; ".join(error.message for error in result.errors) or "no screenshots captured"
            )
            logger.error("Screenshot job %s failed: %s", job_label, error_text)

    logger.info(
        "Screenshot jobs completed: total=%d success=%d failure=%d",
        len(batch_result.results),
        len(batch_result.successes),
        len(batch_result.failures),
    )

    if args.summary_file:
        summary_payload = batch_result.to_dict()
        args.summary_file.parent.mkdir(parents=True, exist_ok=True)
        args.summary_file.write_text(
            json.dumps(summary_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        logger.info("Wrote screenshot summary to %s", args.summary_file)

    return 1 if batch_result.failures else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
