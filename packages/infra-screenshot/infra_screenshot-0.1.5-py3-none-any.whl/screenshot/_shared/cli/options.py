"""Materialise `ScreenshotOptions` from CLI overrides."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from ...models import ScreenshotOptions
from .options_builders import build_from_nested as _build_nested_options
from .options_validate import validate_schema_version
from .schema import ScreenshotCliArgs


def build_options(
    *,
    args: ScreenshotCliArgs,
    css_snippets: Sequence[str],
    js_snippets: Sequence[str],
    overrides: Mapping[str, object] | None = None,
) -> ScreenshotOptions:
    """Return fully-populated ScreenshotOptions for a job."""

    data: dict[str, object] = dict(overrides or {})
    defaults = ScreenshotOptions()

    validate_schema_version(data)
    if data:
        has_nested = any(
            isinstance(data.get(key), dict) for key in ("capture", "browser", "runner")
        )
        if not has_nested:
            raise ValueError(
                "Screenshot option overrides must provide nested "
                "'capture', 'browser', or 'runner' sections."
            )
    return _build_nested_options(data, defaults, args, css_snippets, js_snippets)
