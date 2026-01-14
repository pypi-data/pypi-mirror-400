"""Public API models for screenshot capture.

This module exposes the core public types needed by consumers of the screenshot
package. Internal implementation details are kept in private _models_* modules.
"""

from __future__ import annotations

# Public configuration types
# Internal types needed by some tests/advanced users
# These are intentionally not in __all__ to discourage casual use
from ._models_options import (
    CaptureOptions,
    ScreenshotOptions,
)

# Public result types
from ._models_results import (
    ScreenshotBatchResult,
    ScreenshotCaptureResult,
    ScreenshotJob,
    ScreenshotResourceError,
    ScreenshotResourceOutcome,
    ScreenshotResourceResult,
)

__all__ = [
    # Core configuration
    "ScreenshotOptions",
    "CaptureOptions",
    # Job specification
    "ScreenshotJob",
    # Result types
    "ScreenshotCaptureResult",
    "ScreenshotBatchResult",
    "ScreenshotResourceResult",
    "ScreenshotResourceOutcome",
    "ScreenshotResourceError",
]
