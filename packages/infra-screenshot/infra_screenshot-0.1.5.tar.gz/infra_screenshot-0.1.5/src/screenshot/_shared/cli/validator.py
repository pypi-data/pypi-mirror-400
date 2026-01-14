"""Validation helpers for CLI derived job specs."""

from __future__ import annotations

from ...models import ScreenshotOptions

SUPPORTED_BACKENDS = {"playwright"}

__all__ = ["SUPPORTED_BACKENDS", "validate_backend_choice"]


def validate_backend_choice(selected_backend: str, options: ScreenshotOptions) -> None:
    """Ensure the requested backend is supported for the resolved options."""

    backend = selected_backend.strip().lower()
    if backend not in SUPPORTED_BACKENDS:
        supported = ", ".join(sorted(SUPPORTED_BACKENDS))
        raise ValueError(
            f"backend '{selected_backend}' is not supported yet; available backends: {supported}"
        )
    # Reserved for backend-specific validations (e.g., Selenium constraints).
    _ = options
