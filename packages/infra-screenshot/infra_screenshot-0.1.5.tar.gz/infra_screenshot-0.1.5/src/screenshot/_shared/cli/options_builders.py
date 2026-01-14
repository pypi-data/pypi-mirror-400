"""Typed builders for nested CLI options -> ScreenshotOptions.

Purpose:
- Provide pure functions that assemble `ScreenshotOptions` from already
  validated, typed inputs (nested "v2" schema and CLI arg snapshots).
- Keep `options.py` thin and focused on orchestration/dispatch.

Notes:
- Helpers here (e.g., `ensure_list`, `pick`, `to_float`) are intentionally
  small and side‑effect free to make unit testing straightforward.
- Public entry point: `build_from_nested()`; it returns a fully populated
  `ScreenshotOptions` without mutating its arguments.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from ..._models_options import BrowserCompatOptions, CaptureOptions, RunnerOptions
from ...models import ScreenshotOptions
from .schema import ScreenshotCliArgs

_CHROMIUM_COMPAT_CHOICES = {"low", "medium", "high"}


def ensure_list(value: object | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list | tuple | set):
        return [str(item) for item in value if isinstance(item, str)]
    return [str(value)]


def pick(containers: Sequence[Mapping[str, object]], *keys: str) -> object | None:
    for key in keys:
        for container in containers:
            if key in container and container[key] is not None:
                return container[key]
    return None


def to_float(value: object | None, default: float) -> float:
    if value is None:
        return default
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


def bool_field(
    containers: Sequence[Mapping[str, object]],
    keys: Sequence[str],
    arg_value: bool | None,
    default: bool,
) -> bool:
    raw = pick(containers, *keys)
    if raw is not None:
        return bool(raw)
    if arg_value is not None:
        return bool(arg_value)
    return default


def numeric_field(
    containers: Sequence[Mapping[str, object]],
    keys: Sequence[str],
    *,
    fallback: object | None,
    default: float,
    coerce: Callable[[Any], float],
    minimum: float | None = None,
) -> float:
    raw = pick(containers, *keys)
    if raw is None:
        raw = fallback
    if raw is None:
        raw = default
    value = coerce(raw)
    if minimum is not None:
        value = max(minimum, value)
    return value


def build_from_nested(
    data: Mapping[str, object],
    defaults: ScreenshotOptions,
    args: ScreenshotCliArgs,
    css_snippets: Sequence[str],
    js_snippets: Sequence[str],
) -> ScreenshotOptions:
    capture_data = data.get("capture")
    browser_data = data.get("browser")
    runner_data = data.get("runner")
    capture_data = capture_data if isinstance(capture_data, dict) else {}
    browser_data = browser_data if isinstance(browser_data, dict) else {}
    runner_data = runner_data if isinstance(runner_data, dict) else {}

    max_pages = int(
        numeric_field(
            [capture_data, data],
            ("max_pages",),
            fallback=args.max_pages,
            default=defaults.capture.max_pages,
            coerce=float,
            minimum=1,
        )
    )
    depth = int(
        numeric_field(
            [capture_data, data],
            ("depth",),
            fallback=args.depth,
            default=defaults.capture.depth,
            coerce=float,
            minimum=0,
        )
    )

    viewports_value = pick([capture_data, data], "viewports")
    if viewports_value is None:
        viewports_value = args.viewports or ["desktop"]
    viewports_list = ensure_list(viewports_value)
    if not viewports_list:
        viewports_list = ["desktop"]

    raw_post_nav_wait = pick([capture_data, data], "post_nav_wait_s", "delay")
    post_nav_wait = numeric_field(
        [],
        (),
        fallback=raw_post_nav_wait if raw_post_nav_wait is not None else args.post_nav_wait_s,
        default=defaults.capture.post_nav_wait_s,
        coerce=float,
        minimum=0.0,
    )

    timeout = numeric_field(
        [capture_data, data],
        ("timeout_s", "timeout"),
        fallback=args.timeout_s,
        default=defaults.capture.timeout_s,
        coerce=float,
        minimum=10.0,
    )

    scroll = bool_field([capture_data, data], ("scroll",), args.scroll, defaults.capture.scroll)

    raw_scroll_delay = pick([capture_data, data], "scroll_step_delay_ms", "scroll_step_delay")
    if raw_scroll_delay is None:
        raw_scroll_delay = args.scroll_step_delay_ms
    if raw_scroll_delay is not None:
        scroll_step_delay_ms = int(
            numeric_field(
                [],
                (),
                fallback=raw_scroll_delay,
                default=defaults.capture.scroll_step_delay_ms,
                coerce=float,
                minimum=0.0,
            )
        )
    else:
        scroll_step_delay_ms = defaults.capture.scroll_step_delay_ms

    raw_scroll_steps = pick([capture_data, data], "max_scroll_steps", "scroll_steps")
    if raw_scroll_steps is None:
        raw_scroll_steps = args.max_scroll_steps
    if raw_scroll_steps is not None:
        max_scroll_steps = int(
            numeric_field(
                [],
                (),
                fallback=raw_scroll_steps,
                default=defaults.capture.max_scroll_steps,
                coerce=float,
                minimum=0.0,
            )
        )
    else:
        max_scroll_steps = defaults.capture.max_scroll_steps

    raw_retries = pick([capture_data, data], "max_capture_attempts", "max_retries")
    if raw_retries is None:
        raw_retries = args.max_retries
    if raw_retries is not None:
        max_attempts = int(
            numeric_field(
                [],
                (),
                fallback=raw_retries,
                default=defaults.capture.max_capture_attempts,
                coerce=float,
                minimum=1,
            )
        )
    else:
        max_attempts = defaults.capture.max_capture_attempts

    raw_budget = pick(
        [capture_data, data], "max_total_duration_s", "max_total_duration", "job_budget_s"
    )
    if raw_budget is None:
        raw_budget = args.job_budget_s
    if raw_budget is not None:
        max_total_duration = numeric_field(
            [],
            (),
            fallback=raw_budget,
            default=defaults.capture.max_total_duration_s or 0.0,
            coerce=float,
            minimum=10.0,
        )
    else:
        max_total_duration = None

    raw_viewport_concurrency = pick([capture_data, data], "max_viewport_concurrency")
    if raw_viewport_concurrency is None:
        raw_viewport_concurrency = args.max_viewport_concurrency
    if raw_viewport_concurrency is None:
        max_viewport_concurrency = defaults.capture.max_viewport_concurrency
    else:
        max_viewport_concurrency = int(
            numeric_field(
                [],
                (),
                fallback=raw_viewport_concurrency,
                default=defaults.capture.max_viewport_concurrency,
                coerce=float,
                minimum=1,
            )
        )

    raw_pre_capture = pick([capture_data, data], "pre_capture_wait_s", "settle_timeout")
    if raw_pre_capture is None:
        raw_pre_capture_ms = pick([capture_data, data], "pre_capture_wait_ms")
        if raw_pre_capture_ms is not None:
            raw_pre_capture = to_float(raw_pre_capture_ms, 0.0) / 1000.0
    if raw_pre_capture is None:
        raw_pre_capture = args.pre_capture_wait_s
    settle_timeout = numeric_field(
        [],
        (),
        fallback=raw_pre_capture,
        default=defaults.capture.pre_capture_wait_s,
        coerce=float,
        minimum=0.0,
    )

    full_page = bool_field(
        [capture_data, data], ("full_page",), args.full_page, defaults.capture.full_page
    )

    allow_autoplay = bool_field(
        [browser_data, data],
        ("allow_autoplay",),
        args.allow_autoplay,
        defaults.browser.allow_autoplay,
    )
    hide_overlays = bool_field(
        [browser_data, data],
        ("hide_overlays",),
        args.hide_overlays,
        defaults.browser.hide_overlays,
    )
    reduced_motion = bool_field(
        [browser_data, data],
        ("reduced_motion",),
        args.reduced_motion,
        defaults.browser.reduced_motion,
    )
    mute_media = bool_field(
        [browser_data, data], ("mute_media",), args.mute_media, defaults.browser.mute_media
    )
    disable_animations = bool_field(
        [browser_data, data],
        ("disable_animations",),
        args.disable_animations,
        defaults.browser.disable_animations,
    )
    block_media = bool_field(
        [browser_data, data],
        ("block_media",),
        args.block_media,
        defaults.browser.block_media,
    )

    raw_compat = pick(
        [browser_data, data], "compatibility_level", "chromium_compat", "forgiveness_level"
    )
    if raw_compat is None:
        raw_compat = args.chromium_compat
    if raw_compat is None:
        raw_compat = defaults.browser.compatibility_level
    forgiveness_level = str(raw_compat).strip().lower()
    if forgiveness_level not in _CHROMIUM_COMPAT_CHOICES:
        forgiveness_level = defaults.browser.compatibility_level

    override_user_agent_raw = (
        pick([browser_data], "user_agent")
        or data.get("override_custom_user_agent")
        or data.get("user_agent")
        or args.override_custom_user_agent
        or defaults.browser.user_agent
    )
    override_user_agent = (
        str(override_user_agent_raw) if override_user_agent_raw is not None else None
    )

    extra_styles: list[str] = list(css_snippets)
    runner_styles = pick([runner_data, data], "extra_styles")
    extra_styles.extend(ensure_list(runner_styles))

    extra_init_scripts: list[str] = list(js_snippets)
    runner_scripts = pick([runner_data, data], "extra_init_scripts")
    extra_init_scripts.extend(ensure_list(runner_scripts))

    extra: dict[str, object] = {}
    raw_extra = pick([runner_data, data], "extra")
    if isinstance(raw_extra, dict):
        extra.update(raw_extra)

    playwright_executable_path_raw = pick([runner_data, data], "playwright_executable_path")
    playwright_executable_path = (
        str(playwright_executable_path_raw) if playwright_executable_path_raw is not None else None
    )
    if playwright_executable_path is None:
        playwright_executable_path = args.playwright_executable_path

    capture_opts = CaptureOptions(
        enabled=bool(
            pick([capture_data, data], "enabled")
            if pick([capture_data, data], "enabled") is not None
            else True
        ),
        max_pages=max_pages,
        depth=depth,
        viewports=tuple(viewports_list or ["desktop"]),
        post_nav_wait_s=post_nav_wait,
        timeout_s=timeout,
        max_total_duration_s=max_total_duration,
        max_capture_attempts=max_attempts,
        max_viewport_concurrency=max_viewport_concurrency,
        scroll=scroll,
        scroll_step_delay_ms=scroll_step_delay_ms,
        max_scroll_steps=max_scroll_steps,
        full_page=full_page,
        pre_capture_wait_s=settle_timeout,
    )

    browser_opts = BrowserCompatOptions(
        allow_autoplay=allow_autoplay,
        hide_overlays=hide_overlays,
        reduced_motion=reduced_motion,
        disable_animations=disable_animations,
        mute_media=mute_media,
        block_media=block_media,
        compatibility_level=forgiveness_level,
        user_agent=override_user_agent,
    )

    runner_opts = RunnerOptions(
        extra_styles=tuple(extra_styles),
        extra_init_scripts=tuple(extra_init_scripts),
        playwright_executable_path=playwright_executable_path,
        extra=extra,
    )

    return ScreenshotOptions(capture=capture_opts, browser=browser_opts, runner=runner_opts)
