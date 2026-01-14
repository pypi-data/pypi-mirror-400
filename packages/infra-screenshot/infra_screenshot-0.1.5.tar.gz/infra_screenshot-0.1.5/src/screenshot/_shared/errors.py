"""Structured error types shared within the screenshot package."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


@dataclass(frozen=True)
class ScreenshotError:
    """Typed error emitted during screenshot capture."""

    error_type: str
    message: str
    retryable: bool = False
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "error_type": self.error_type,
            "message": self.message,
            "retryable": self.retryable,
            "details": dict(self.details),
        }

    def __str__(self) -> str:
        return self.message


def make_error(
    error_type: str,
    message: str,
    *,
    retryable: bool = False,
    details: dict[str, object] | None = None,
) -> ScreenshotError:
    """Factory that normalises inputs into a ScreenshotError."""

    return ScreenshotError(
        error_type=error_type,
        message=message,
        retryable=retryable,
        details=dict(details or {}),
    )


class ErrorCategory(str, Enum):
    TIMEOUT = "screenshot.timeout"
    NAVIGATION = "screenshot.navigation"
    BROWSER = "screenshot.browser"
    STORAGE = "screenshot.storage"
    UNKNOWN = "screenshot.unknown"

    @classmethod
    def from_error_type(cls, error_type: str | None) -> ErrorCategory:
        normalized = (error_type or "").lower().strip()
        if not normalized:
            return cls.UNKNOWN
        if "timeout" in normalized:
            return cls.TIMEOUT
        if "navigation" in normalized:
            return cls.NAVIGATION
        if "browser" in normalized:
            return cls.BROWSER
        if "storage" in normalized:
            return cls.STORAGE
        return cls.UNKNOWN
