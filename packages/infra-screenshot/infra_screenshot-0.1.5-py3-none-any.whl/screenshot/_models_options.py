from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import TypeAlias

from .defaults import DEFAULTS

"""Capture/browser/runner option dataclasses and their serialization helpers."""

ViewportSpec: TypeAlias = str | dict[str, object]
DEFAULT_VIEWPORTS: tuple[ViewportSpec, ...] = ("desktop",)
OPTIONS_SCHEMA_VERSION = "screenshot_options/v2"


def _to_int(val: object | None, default: int) -> int:
    if isinstance(val, bool):
        return int(val)
    if isinstance(val, int | float):
        return int(val)
    if isinstance(val, str):
        try:
            return int(val)
        except Exception:
            return default
    return default


def _to_float(val: object | None, default: float) -> float:
    if isinstance(val, int | float):
        return float(val)
    if isinstance(val, str):
        try:
            return float(val)
        except Exception:
            return default
    return default


@dataclass(frozen=True, kw_only=True, slots=True)
class CaptureOptions:
    enabled: bool = False
    max_pages: int = 1
    depth: int = 0
    viewports: tuple[ViewportSpec, ...] = DEFAULT_VIEWPORTS
    post_nav_wait_s: float = 2.5
    timeout_s: float = 60.0
    max_total_duration_s: float | None = None
    max_capture_attempts: int = 3
    max_viewport_concurrency: int = 1
    scroll: bool = False
    scroll_step_delay_ms: int = DEFAULTS.scroll_step_delay_ms
    max_scroll_steps: int = DEFAULTS.max_scroll_steps
    full_page: bool = False
    pre_capture_wait_s: float = 1.5

    def __post_init__(self) -> None:
        if self.max_pages < 1:
            raise ValueError(f"max_pages must be >= 1, got {self.max_pages}")
        if self.depth < 0:
            raise ValueError(f"depth must be >= 0, got {self.depth}")
        if not self.viewports:
            raise ValueError("At least one viewport must be configured")
        for viewport in self.viewports:
            if not isinstance(viewport, str | dict):
                raise TypeError(
                    f"Viewport entries must be str or dict, got {type(viewport).__name__}"
                )
        if self.timeout_s <= 0:
            raise ValueError(f"timeout_s must be > 0, got {self.timeout_s}")
        if self.max_total_duration_s is not None and self.max_total_duration_s <= 0:
            raise ValueError(
                f"max_total_duration_s must be > 0 when set, got {self.max_total_duration_s}"
            )
        if self.max_capture_attempts < 1:
            raise ValueError(f"max_capture_attempts must be >= 1, got {self.max_capture_attempts}")
        if self.max_viewport_concurrency < 1:
            raise ValueError(
                f"max_viewport_concurrency must be >= 1, got {self.max_viewport_concurrency}"
            )
        if self.scroll_step_delay_ms < 0:
            raise ValueError(f"scroll_step_delay_ms must be >= 0, got {self.scroll_step_delay_ms}")
        if self.max_scroll_steps < 0:
            raise ValueError(f"max_scroll_steps must be >= 0, got {self.max_scroll_steps}")
        if self.post_nav_wait_s < 0:
            raise ValueError(f"post_nav_wait_s must be >= 0, got {self.post_nav_wait_s}")
        if self.pre_capture_wait_s < 0:
            raise ValueError(f"pre_capture_wait_s must be >= 0, got {self.pre_capture_wait_s}")

    def merged_viewports(
        self, defaults: dict[str, dict[str, object]]
    ) -> dict[str, dict[str, object]]:
        presets: dict[str, dict[str, object]] = {}
        for viewport in self.viewports:
            if isinstance(viewport, str):
                preset = defaults.get(viewport)
                if not preset:
                    continue
                presets[viewport] = preset
            elif isinstance(viewport, dict):
                name = viewport.get("name")
                if not isinstance(name, str) or not name:
                    continue
                presets[name] = {
                    "viewport": viewport.get("viewport", defaults.get(name, {}).get("viewport")),
                    "device_scale_factor": viewport.get(
                        "device_scale_factor",
                        defaults.get(name, {}).get("device_scale_factor", 1.0),
                    ),
                    "is_mobile": viewport.get(
                        "is_mobile", defaults.get(name, {}).get("is_mobile", False)
                    ),
                    "has_touch": viewport.get(
                        "has_touch", defaults.get(name, {}).get("has_touch", False)
                    ),
                }
        return presets


@dataclass(kw_only=True, slots=True)
class BrowserCompatOptions:
    allow_autoplay: bool = True
    hide_overlays: bool = True
    reduced_motion: bool = True
    disable_animations: bool = True
    mute_media: bool = True
    block_media: bool = False
    compatibility_level: str = "high"
    user_agent: str | None = None

    def __post_init__(self) -> None:
        if not self.compatibility_level or not self.compatibility_level.strip():
            raise ValueError("compatibility_level must be a non-empty string")
        object.__setattr__(self, "compatibility_level", self.compatibility_level.strip().lower())


@dataclass(kw_only=True, slots=True)
class RunnerOptions:
    extra_styles: tuple[str, ...] = field(default_factory=tuple)
    extra_init_scripts: tuple[str, ...] = field(default_factory=tuple)
    playwright_executable_path: str | None = None
    extra: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "extra_styles", tuple(str(style) for style in self.extra_styles))
        object.__setattr__(
            self,
            "extra_init_scripts",
            tuple(str(script) for script in self.extra_init_scripts),
        )
        object.__setattr__(self, "extra", MappingProxyType(dict(self.extra)))


@dataclass(kw_only=True, slots=True)
class ScreenshotOptions:
    capture: CaptureOptions = field(default_factory=CaptureOptions)
    browser: BrowserCompatOptions = field(default_factory=BrowserCompatOptions)
    runner: RunnerOptions = field(default_factory=RunnerOptions)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ScreenshotOptions:
        schema_version = data.get("schema_version")
        if schema_version is not None:
            normalized = str(schema_version).strip()
            if normalized != OPTIONS_SCHEMA_VERSION:
                raise ValueError(
                    f"Expected schema {OPTIONS_SCHEMA_VERSION}, got {normalized or 'unknown'}"
                )

        capture_val = data.get("capture")
        browser_val = data.get("browser")
        runner_val = data.get("runner")

        capture_raw = capture_val if isinstance(capture_val, dict) else None
        browser_raw = browser_val if isinstance(browser_val, dict) else None
        runner_raw = runner_val if isinstance(runner_val, dict) else None

        if not any(section is not None for section in (capture_raw, browser_raw, runner_raw)):
            raise ValueError(
                "ScreenshotOptions.from_dict expects at least one of "
                "'capture', 'browser', or 'runner'."
            )

        capture = _capture_from_nested_dict(capture_raw)
        browser = _browser_from_nested_dict(browser_raw)
        runner = _runner_from_nested_dict(runner_raw)
        return cls(capture=capture, browser=browser, runner=runner)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": OPTIONS_SCHEMA_VERSION,
            "capture": _capture_to_dict(self.capture),
            "browser": _browser_to_dict(self.browser),
            "runner": _runner_to_dict(self.runner),
        }


def _capture_from_nested_dict(raw: dict[str, object] | None) -> CaptureOptions:
    payload = dict(raw or {})
    viewports_val = payload.get("viewports")
    viewports: tuple[ViewportSpec, ...] = (
        tuple(v for v in viewports_val)
        if isinstance(viewports_val, list | tuple) and viewports_val
        else DEFAULT_VIEWPORTS
    )
    return CaptureOptions(
        enabled=bool(payload.get("enabled", False)),
        max_pages=_to_int(payload.get("max_pages"), 1),
        depth=_to_int(payload.get("depth"), 0),
        viewports=viewports,
        post_nav_wait_s=_to_float(payload.get("post_nav_wait_s"), 2.5),
        timeout_s=_to_float(payload.get("timeout_s"), 60.0),
        max_total_duration_s=_to_float(payload.get("max_total_duration_s"), 0.0) or None,
        max_capture_attempts=_to_int(payload.get("max_capture_attempts"), 3),
        max_viewport_concurrency=_to_int(payload.get("max_viewport_concurrency"), 1),
        scroll=bool(payload.get("scroll", False)),
        scroll_step_delay_ms=_to_int(
            payload.get("scroll_step_delay_ms"), DEFAULTS.scroll_step_delay_ms
        ),
        max_scroll_steps=_to_int(payload.get("max_scroll_steps"), DEFAULTS.max_scroll_steps),
        full_page=bool(payload.get("full_page", False)),
        pre_capture_wait_s=_to_float(payload.get("pre_capture_wait_s"), 1.5),
    )


def _browser_from_nested_dict(raw: dict[str, object] | None) -> BrowserCompatOptions:
    payload = dict(raw or {})
    compat = payload.get("compatibility_level")
    level = str(compat).strip().lower() if isinstance(compat, str) else "high"
    return BrowserCompatOptions(
        allow_autoplay=bool(payload.get("allow_autoplay", True)),
        hide_overlays=bool(payload.get("hide_overlays", True)),
        reduced_motion=bool(payload.get("reduced_motion", True)),
        disable_animations=bool(payload.get("disable_animations", True)),
        mute_media=bool(payload.get("mute_media", True)),
        block_media=bool(payload.get("block_media", False)),
        compatibility_level=level,
        user_agent=(
            str(payload.get("user_agent")) if isinstance(payload.get("user_agent"), str) else None
        ),
    )


def _runner_from_nested_dict(raw: dict[str, object] | None) -> RunnerOptions:
    payload = dict(raw or {})
    styles_val = payload.get("extra_styles")
    scripts_val = payload.get("extra_init_scripts")
    styles = tuple(str(s) for s in styles_val) if isinstance(styles_val, list | tuple) else tuple()
    scripts = (
        tuple(str(s) for s in scripts_val) if isinstance(scripts_val, list | tuple) else tuple()
    )
    pe_path = payload.get("playwright_executable_path")
    extra_payload = payload.get("extra")
    extra: dict[str, object] = dict(extra_payload) if isinstance(extra_payload, dict) else {}
    return RunnerOptions(
        extra_styles=styles,
        extra_init_scripts=scripts,
        playwright_executable_path=str(pe_path) if isinstance(pe_path, str | Path) else None,
        extra=extra,
    )


def _capture_to_dict(options: CaptureOptions) -> dict[str, object]:
    return {
        "enabled": options.enabled,
        "max_pages": options.max_pages,
        "depth": options.depth,
        "viewports": [vp for vp in options.viewports],
        "post_nav_wait_s": options.post_nav_wait_s,
        "timeout_s": options.timeout_s,
        "max_total_duration_s": options.max_total_duration_s,
        "max_capture_attempts": options.max_capture_attempts,
        "max_viewport_concurrency": options.max_viewport_concurrency,
        "scroll": options.scroll,
        "scroll_step_delay_ms": options.scroll_step_delay_ms,
        "max_scroll_steps": options.max_scroll_steps,
        "full_page": options.full_page,
        "pre_capture_wait_s": options.pre_capture_wait_s,
    }


def _browser_to_dict(options: BrowserCompatOptions) -> dict[str, object]:
    return {
        "allow_autoplay": options.allow_autoplay,
        "hide_overlays": options.hide_overlays,
        "reduced_motion": options.reduced_motion,
        "disable_animations": options.disable_animations,
        "mute_media": options.mute_media,
        "block_media": options.block_media,
        "compatibility_level": options.compatibility_level,
        "user_agent": options.user_agent,
    }


def _runner_to_dict(options: RunnerOptions) -> dict[str, object]:
    return {
        "extra_styles": list(options.extra_styles),
        "extra_init_scripts": list(options.extra_init_scripts),
        "playwright_executable_path": options.playwright_executable_path,
        "extra": dict(options.extra),
    }
