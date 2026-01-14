"""Centralized defaults and env-driven settings for screenshot package.

Use these helpers to avoid magic numbers scattered across modules and to
support simple environment overrides in CI or operational contexts.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _int_env(name: str, default: int) -> int:
    try:
        raw = os.getenv(name)
        return int(raw) if raw is not None else default
    except Exception:
        return default


def _float_env(name: str, default: float) -> float:
    try:
        raw = os.getenv(name)
        return float(raw) if raw is not None else default
    except Exception:
        return default


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ScreenshotDefaults:
    scroll_step_delay_ms: int = 250
    max_scroll_steps: int = 15
    playwright_max_capture_attempts: int = 3
    retry_backoff_s: float = 0.5
    retry_max_backoff_s: float = 5.0
    enable_timing: bool = False

    @classmethod
    def load(cls) -> ScreenshotDefaults:
        return cls(
            scroll_step_delay_ms=_int_env("SCREENSHOT_SCROLL_STEP_DELAY_MS", 250),
            max_scroll_steps=_int_env("SCREENSHOT_MAX_SCROLL_STEPS", 15),
            playwright_max_capture_attempts=_int_env("PLAYWRIGHT_CAPTURE_MAX_ATTEMPTS", 3),
            retry_backoff_s=_float_env("SCREENSHOT_RETRY_BACKOFF_S", 0.5),
            retry_max_backoff_s=_float_env("SCREENSHOT_RETRY_MAX_BACKOFF_S", 5.0),
            enable_timing=_bool_env("SCREENSHOT_ENABLE_TIMING", False),
        )


DEFAULTS = ScreenshotDefaults.load()
