"""Internal utilities shared within the screenshot package.

These helpers reside in `_internal` so we can move logic outside of the
public dataclasses while keeping the public API surface intact.
"""

from __future__ import annotations

from .resource_transformer import (
    from_capture_result,
    generate_screenshot_config_key,
    per_viewport_resources,
)

__all__ = [
    "from_capture_result",
    "per_viewport_resources",
    "generate_screenshot_config_key",
]
