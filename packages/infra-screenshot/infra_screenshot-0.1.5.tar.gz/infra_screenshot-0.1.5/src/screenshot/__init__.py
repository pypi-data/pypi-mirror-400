"""Shared models and services for screenshot capture backends."""

from __future__ import annotations

__version__ = "0.1.5"

import logging

from ._shared.storage import (
    AsyncStorageBackend,
    CloudStorageBackend,
    LocalStorageBackend,
    StorageBackend,
)
from ._shared.types import ScreenshotJobSpec, ScreenshotMetadata
from .models import (
    ScreenshotBatchResult,
    ScreenshotCaptureResult,
    ScreenshotJob,
    ScreenshotOptions,
    ScreenshotResourceError,
    ScreenshotResourceOutcome,
    ScreenshotResourceResult,
)
from .playwright_runner import KNOWN_VIEWPORTS, capture_screenshots, capture_screenshots_async
from .selenium_runner import capture_screenshots_async as capture_screenshots_async_selenium
from .service import ScreenshotBackend, ScreenshotService

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "ScreenshotBatchResult",
    "ScreenshotCaptureResult",
    "ScreenshotJob",
    "ScreenshotOptions",
    "ScreenshotResourceError",
    "ScreenshotResourceOutcome",
    "ScreenshotResourceResult",
    "ScreenshotJobSpec",
    "ScreenshotMetadata",
    "ScreenshotBackend",
    "ScreenshotService",
    "KNOWN_VIEWPORTS",
    "LocalStorageBackend",
    "StorageBackend",
    "CloudStorageBackend",
    "AsyncStorageBackend",
    "capture_screenshots",
    "capture_screenshots_async",
    "capture_screenshots_async_selenium",
]
