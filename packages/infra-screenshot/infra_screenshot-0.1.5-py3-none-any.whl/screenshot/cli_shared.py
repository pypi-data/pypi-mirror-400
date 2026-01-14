"""Argument parser helpers shared by screenshot-related CLIs.

These helpers keep the CLI UX consistent across the standalone screenshot
tooling and other entry points by centralising the shared argument
groups and lightweight parsing utilities.

Example:
    >>> parser = argparse.ArgumentParser(prog="demo")
    >>> add_job_arguments(parser, include_output_dir=False)
    >>> "--backend" in parser.format_help()
    True
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from ._shared.cli.arguments import add_programmatic_job_arguments
from .cli_config import apply_config_to_parser, load_cli_config
from .cli_utils import ScreenshotCliArgs

_CHROMIUM_COMPAT_CHOICES = ("low", "medium", "high")


def _normalize_chromium_compat(value: str) -> str:
    """Sanitise chromium compatibility input and enforce valid choices."""

    text = str(value).strip().lower()
    if text not in _CHROMIUM_COMPAT_CHOICES:
        raise argparse.ArgumentTypeError(
            f"expected one of {', '.join(_CHROMIUM_COMPAT_CHOICES)}, got '{value}'"
        )
    return text


def add_job_arguments(
    parser: argparse.ArgumentParser,
    *,
    include_output_dir: bool,
    config_path: Path | None = None,
    preset: str | None = None,
    use_config: bool = False,
) -> None:
    """Add shared screenshot job arguments to an argparse parser.

    Args:
        parser: Target `argparse.ArgumentParser` or sub-parser.
        include_output_dir: Whether to add the required `--output-dir` flag
            (only relevant for local execution commands).
        config_path: Optional explicit YAML configuration to load.
        preset: Optional preset defined in the YAML file.
        use_config: Force config-driven mode using the default YAML file.
    """

    if use_config or config_path or preset:
        config = load_cli_config(config_path)
        if include_output_dir and not preset:
            exclude_args: tuple[str, ...] = ()
        elif include_output_dir:
            exclude_args = ()
        else:
            exclude_args = () if preset else ("output_dir",)
        apply_config_to_parser(parser, config, exclude_args=exclude_args, preset=preset)
    else:
        add_programmatic_job_arguments(
            parser,
            include_output_dir=include_output_dir,
            normalize_chromium_compat=_normalize_chromium_compat,
        )


def build_cli_args(args: argparse.Namespace) -> ScreenshotCliArgs:
    """Build structured CLI arguments from an argparse namespace.

    Args:
        args: Parsed `argparse.Namespace` produced by the screenshot CLI parsers.

    Returns:
        `ScreenshotCliArgs` instance ready for downstream job collection.

    Example:
        >>> namespace = argparse.Namespace(
        ...     urls=["https://example.com"],
        ...     site_ids=["demo"],
        ...     partition_date=None,
        ...     max_pages=None,
        ...     depth=None,
        ...     viewports=None,
        ...     post_nav_wait_s=None,
        ...     pre_capture_wait_s=None,
        ...     timeout=None,
        ...     max_retries=None,
        ...     job_budget_s=None,
        ...     scroll=None,
        ...     allow_autoplay=None,
        ...     hide_overlays=None,
        ...     reduced_motion=None,
        ...     full_page=None,
        ...     mute_media=None,
        ...     disable_animations=None,
        ...     block_media=None,
        ...     extra_css=None,
        ...     extra_js=None,
        ...     chromium_compat=None,
        ...     max_viewport_concurrency=None,
        ...     override_custom_user_agent=None,
        ...     playwright_executable_path=None,
        ...     backend="playwright",
        ... )
        >>> result = build_cli_args(namespace)
        >>> result.max_pages
        5
    """

    max_pages = getattr(args, "max_pages", None)
    if max_pages is None:
        max_pages = 5

    depth = getattr(args, "depth", None)
    if depth is None:
        depth = 1

    viewports_value = getattr(args, "viewports", None)
    viewports = _ensure_sequence(viewports_value)
    if not viewports:
        viewports = ("desktop",)

    post_nav_wait = getattr(args, "post_nav_wait_s", None)
    if post_nav_wait is None:
        post_nav_wait = 6.0

    pre_capture_wait_s = getattr(args, "pre_capture_wait_s", None)
    if pre_capture_wait_s is None:
        pre_capture_wait_s = 2.5

    job_budget_s = getattr(args, "job_budget_s", None)

    timeout_value = getattr(args, "timeout", None)
    if timeout_value is None:
        timeout_value = 60.0

    max_retries = getattr(args, "max_retries", None)

    multi_css = getattr(args, "extra_css", None)
    if multi_css is None:
        extra_css_paths: Sequence[Path] = ()
    elif isinstance(multi_css, list | tuple):
        extra_css_paths = tuple(multi_css)
    else:
        extra_css_paths = (multi_css,)

    multi_js = getattr(args, "extra_js", None)
    if multi_js is None:
        extra_js_paths: Sequence[Path] = ()
    elif isinstance(multi_js, list | tuple):
        extra_js_paths = tuple(multi_js)
    else:
        extra_js_paths = (multi_js,)

    return ScreenshotCliArgs(
        input=getattr(args, "input", None),
        urls=_ensure_sequence(getattr(args, "urls", ())),
        site_ids=_ensure_sequence(getattr(args, "site_ids", ())),
        partition_date=getattr(args, "partition_date", None),
        max_pages=max_pages,
        depth=depth,
        viewports=viewports,
        post_nav_wait_s=post_nav_wait,
        timeout_s=timeout_value,
        max_retries=max_retries,
        job_budget_s=job_budget_s,
        scroll=getattr(args, "scroll", None),
        scroll_step_delay_ms=getattr(args, "scroll_step_delay_ms", None),
        max_scroll_steps=getattr(args, "max_scroll_steps", None),
        allow_autoplay=getattr(args, "allow_autoplay", None),
        hide_overlays=getattr(args, "hide_overlays", None),
        reduced_motion=getattr(args, "reduced_motion", None),
        full_page=getattr(args, "full_page", None),
        pre_capture_wait_s=pre_capture_wait_s,
        mute_media=getattr(args, "mute_media", None),
        disable_animations=getattr(args, "disable_animations", None),
        block_media=getattr(args, "block_media", None),
        extra_css_paths=extra_css_paths,
        extra_js_paths=extra_js_paths,
        chromium_compat=getattr(args, "chromium_compat", None),
        max_viewport_concurrency=getattr(args, "max_viewport_concurrency", None),
        override_custom_user_agent=getattr(args, "override_custom_user_agent", None),
        playwright_executable_path=getattr(args, "playwright_executable_path", None),
        backend=str(getattr(args, "backend", "playwright")).strip().lower(),
    )


def _ensure_sequence(values: Sequence[str] | None) -> Sequence[str]:
    return tuple(values or ())
