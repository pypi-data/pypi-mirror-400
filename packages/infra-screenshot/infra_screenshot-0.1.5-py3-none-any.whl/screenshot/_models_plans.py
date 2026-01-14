"""Derived plan dataclasses consumed by capture backends along with serialisation helpers."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ._models_options import OPTIONS_SCHEMA_VERSION


@dataclass(frozen=True, kw_only=True, slots=True)
class CapturePlan:
    """Sanitized capture plan consumed by screenshot runners."""

    max_pages: int
    depth: int
    delay_ms: int
    viewport_specs: dict[str, dict[str, object]]
    viewport_details: list[dict[str, object]]
    primary_viewport: str
    timeout_sec: float
    max_total_duration_sec: float
    max_capture_attempts: int
    max_viewport_concurrency: int
    scroll_enabled: bool
    scroll_step_delay_ms: int
    max_scroll_steps: int
    full_page_capture: bool
    settle_timeout_ms: int


@dataclass(frozen=True, kw_only=True, slots=True)
class BrowserPlan:
    """Browser compatibility directives produced by options sanitiser."""

    allow_autoplay: bool
    hide_overlays: bool
    reduced_motion: bool
    disable_animations: bool
    mute_media: bool
    block_media: bool
    compatibility_level: str
    user_agent: str | None


@dataclass(frozen=True, kw_only=True, slots=True)
class RunnerPlan:
    """Runtime directives (styles/scripts/extra payload) for runner launch."""

    extra_styles: Sequence[str]
    extra_init_scripts: Sequence[str]
    navigation_strategies: Sequence[dict[str, object]]
    playwright_executable_path: str | None
    extra: dict[str, object]


@dataclass(frozen=True, kw_only=True, slots=True)
class SanitizedPlans:
    """Container bundling capture/browser/runner plans for runners."""

    capture: CapturePlan
    browser: BrowserPlan
    runner: RunnerPlan

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": OPTIONS_SCHEMA_VERSION,
            "capture": {
                "max_pages": self.capture.max_pages,
                "depth": self.capture.depth,
                "delay_ms": self.capture.delay_ms,
                "viewport_specs": dict(self.capture.viewport_specs),
                "viewport_details": list(self.capture.viewport_details),
                "primary_viewport": self.capture.primary_viewport,
                "timeout_sec": self.capture.timeout_sec,
                "max_total_duration_sec": self.capture.max_total_duration_sec,
                "max_capture_attempts": self.capture.max_capture_attempts,
                "max_viewport_concurrency": self.capture.max_viewport_concurrency,
                "scroll_enabled": self.capture.scroll_enabled,
                "scroll_step_delay_ms": self.capture.scroll_step_delay_ms,
                "max_scroll_steps": self.capture.max_scroll_steps,
                "full_page_capture": self.capture.full_page_capture,
                "settle_timeout_ms": self.capture.settle_timeout_ms,
            },
            "browser": {
                "allow_autoplay": self.browser.allow_autoplay,
                "hide_overlays": self.browser.hide_overlays,
                "reduced_motion": self.browser.reduced_motion,
                "disable_animations": self.browser.disable_animations,
                "mute_media": self.browser.mute_media,
                "block_media": self.browser.block_media,
                "compatibility_level": self.browser.compatibility_level,
                "user_agent": self.browser.user_agent,
            },
            "runner": {
                "extra_styles": list(self.runner.extra_styles),
                "extra_init_scripts": list(self.runner.extra_init_scripts),
                "navigation_strategies": list(self.runner.navigation_strategies),
                "playwright_executable_path": self.runner.playwright_executable_path,
                "extra": dict(self.runner.extra),
            },
        }
