"""Programmatic CLI argument builders shared by screenshot entry points."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

__all__ = ["add_programmatic_job_arguments", "_parse_bool"]


def _parse_bool(value: str | bool | None) -> bool:
    if value is None:
        return True
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"expected boolean value, got {value!r}")


def add_programmatic_job_arguments(
    parser: argparse.ArgumentParser,
    *,
    include_output_dir: bool,
    normalize_chromium_compat: Callable[[str], str],
) -> None:
    """Add programmatic job arguments used when config-driven parsing is disabled."""

    parser.add_argument(
        "--urls",
        action="append",
        dest="urls",
        metavar="URL",
        help="Website URL to capture (repeat flag to capture multiple sites)",
    )
    parser.add_argument(
        "--job-id",
        action="append",
        dest="site_ids",
        help="Identifier to use for the corresponding URL (repeatable; defaults to derived name)",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help='Optional JSONL file with objects {"url": ..., "job_id": ...}',
    )
    parser.add_argument(
        "--backend",
        choices=("playwright", "selenium"),
        default="playwright",
        help="Screenshot backend to use (default: playwright).",
    )

    if include_output_dir:
        parser.add_argument(
            "--output-dir",
            type=Path,
            required=True,
            help="Directory where screenshots and metadata will be stored",
        )

    parser.add_argument(
        "--partition-date",
        type=str,
        help="Optional partition date (YYYY-MM-DD) to embed in metadata",
    )
    parser.add_argument(
        "--max-pages",
        dest="max_pages",
        type=int,
        help="Maximum number of pages to capture per site (default: 5)",
    )
    parser.add_argument(
        "--depth",
        dest="depth",
        type=int,
        help="Maximum link depth to follow when capturing screenshots (default: 1)",
    )
    parser.add_argument(
        "--viewports",
        dest="viewports",
        nargs="+",
        help="Viewport presets for screenshot capture (default: desktop)",
    )
    parser.add_argument(
        "--post-nav-wait-s",
        dest="post_nav_wait_s",
        type=float,
        help="Seconds to wait after navigation before scripted settling (default: 6).",
    )
    parser.add_argument(
        "--timeout-s",
        dest="timeout",
        type=float,
        help="Timeout in seconds for each page capture attempt (default: 60).",
    )
    parser.add_argument(
        "--max-retries",
        dest="max_retries",
        type=int,
        help=(
            "Maximum capture retries per viewport (default: 3 or PLAYWRIGHT_CAPTURE_MAX_ATTEMPTS)."
        ),
    )
    parser.add_argument(
        "--job-budget-s",
        dest="job_budget_s",
        type=float,
        help="Overall time budget in seconds per job before following new links.",
    )
    parser.add_argument(
        "--max-viewport-concurrency",
        dest="max_viewport_concurrency",
        type=int,
        help="Maximum number of viewports captured concurrently (default: 3).",
    )
    parser.add_argument(
        "--scroll",
        dest="scroll",
        type=_parse_bool,
        metavar="{true|false}",
        help="Enable or disable pre-capture scrolling (default: true).",
    )
    parser.add_argument(
        "--scroll-step-delay-ms",
        dest="scroll_step_delay_ms",
        type=int,
        help="Delay between scroll steps in milliseconds (default: 250).",
    )
    parser.add_argument(
        "--max-scroll-steps",
        dest="max_scroll_steps",
        type=int,
        help="Maximum scroll iterations per capture (default: 15).",
    )

    parser.add_argument(
        "--allow-autoplay",
        dest="allow_autoplay",
        nargs="?",
        const="true",
        type=_parse_bool,
        help="Control Chromium autoplay allowance (default: true).",
    )

    parser.add_argument(
        "--hide-overlays",
        dest="hide_overlays",
        nargs="?",
        const="true",
        type=_parse_bool,
        help="Control overlay-hiding CSS injection (default: true).",
    )

    parser.add_argument(
        "--reduced-motion",
        dest="reduced_motion",
        nargs="?",
        const="true",
        type=_parse_bool,
        help="Force prefers-reduced-motion media emulation (default: true).",
    )

    parser.add_argument(
        "--full-page",
        dest="full_page",
        nargs="?",
        const="true",
        type=_parse_bool,
        help="Capture full-page screenshots (default: true). Pass false for viewport-only.",
    )

    parser.add_argument(
        "--mute-media",
        dest="mute_media",
        nargs="?",
        const="true",
        type=_parse_bool,
        help="Force media elements muted during capture (default: true).",
    )

    parser.add_argument(
        "--disable-animations",
        dest="disable_animations",
        nargs="?",
        const="true",
        type=_parse_bool,
        help="Disable CSS animations and transitions before capture (default: true).",
    )

    parser.add_argument(
        "--block-media",
        dest="block_media",
        nargs="?",
        const="true",
        type=_parse_bool,
        help="Block heavyweight media requests such as video/audio (default: false).",
    )

    parser.add_argument(
        "--pre-capture-wait-s",
        dest="pre_capture_wait_s",
        type=float,
        help="Seconds to wait after scrolling/settling before capturing (default: 2.5).",
    )
    parser.add_argument(
        "--extra-css",
        dest="extra_css",
        type=Path,
        action="append",
        help="Path to CSS snippet injected before capture (repeatable).",
    )
    parser.add_argument(
        "--extra-js",
        dest="extra_js",
        type=Path,
        action="append",
        help="Path to JS snippet executed before page scripts (repeatable).",
    )
    parser.add_argument(
        "--override-custom-user-agent",
        dest="override_custom_user_agent",
        type=str,
        help="Override the browser User-Agent string that Playwright would normally supply.",
    )
    parser.add_argument(
        "--playwright-executable-path",
        dest="playwright_executable_path",
        type=str,
        help="Override the Playwright Chromium executable path.",
    )
    parser.add_argument(
        "--chromium-compat",
        dest="chromium_compat",
        type=normalize_chromium_compat,
        help="Chromium compatibility profile (default: high).",
    )

    parser.set_defaults(
        max_pages=None,
        depth=None,
        viewports=None,
        post_nav_wait_s=None,
        timeout=None,
        max_retries=None,
        job_budget_s=None,
        scroll=None,
        allow_autoplay=None,
        hide_overlays=None,
        reduced_motion=None,
        full_page=None,
        mute_media=None,
        disable_animations=None,
        block_media=None,
        pre_capture_wait_s=None,
        extra_css=None,
        extra_js=None,
        chromium_compat=None,
        max_viewport_concurrency=None,
        override_custom_user_agent=None,
        playwright_executable_path=None,
        backend="playwright",
    )
