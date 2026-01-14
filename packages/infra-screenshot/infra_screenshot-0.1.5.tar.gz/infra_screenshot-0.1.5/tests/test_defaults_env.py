from __future__ import annotations

import math

import pytest

from screenshot import defaults


def test_defaults_respect_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCREENSHOT_SCROLL_STEP_DELAY_MS", "123")
    monkeypatch.setenv("SCREENSHOT_MAX_SCROLL_STEPS", "5")
    monkeypatch.setenv("PLAYWRIGHT_CAPTURE_MAX_ATTEMPTS", "7")
    monkeypatch.setenv("SCREENSHOT_RETRY_BACKOFF_S", "0.75")
    monkeypatch.setenv("SCREENSHOT_RETRY_MAX_BACKOFF_S", "9.5")
    monkeypatch.setenv("SCREENSHOT_ENABLE_TIMING", "true")

    loaded = defaults.ScreenshotDefaults.load()

    assert loaded.scroll_step_delay_ms == 123
    assert loaded.max_scroll_steps == 5
    assert loaded.playwright_max_capture_attempts == 7
    assert loaded.retry_backoff_s == 0.75
    assert loaded.retry_max_backoff_s == 9.5
    assert loaded.enable_timing is True


def test_defaults_fall_back_on_invalid_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCREENSHOT_SCROLL_STEP_DELAY_MS", "not-an-int")
    monkeypatch.setenv("SCREENSHOT_RETRY_BACKOFF_S", "NaN")

    loaded = defaults.ScreenshotDefaults.load()

    assert loaded.scroll_step_delay_ms == 250
    assert math.isnan(loaded.retry_backoff_s)
