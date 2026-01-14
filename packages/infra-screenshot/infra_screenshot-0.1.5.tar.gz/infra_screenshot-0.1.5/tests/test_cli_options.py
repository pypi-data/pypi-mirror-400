import pytest

from screenshot._shared.cli.options import build_options
from screenshot._shared.cli.schema import ScreenshotCliArgs


def _make_args() -> ScreenshotCliArgs:
    return ScreenshotCliArgs(
        input=None,
        urls=("https://example.com",),
        site_ids=("demo",),
        partition_date=None,
        max_pages=1,
        depth=0,
        viewports=("desktop",),
        post_nav_wait_s=1.0,
        timeout_s=30.0,
        max_retries=1,
        job_budget_s=None,
        scroll=None,
        allow_autoplay=None,
        hide_overlays=None,
        reduced_motion=None,
        full_page=None,
        pre_capture_wait_s=None,
        mute_media=None,
        disable_animations=None,
        block_media=None,
        extra_css_paths=(),
        extra_js_paths=(),
        chromium_compat=None,
        max_viewport_concurrency=None,
        override_custom_user_agent=None,
        playwright_executable_path=None,
        backend="playwright",
    )


def test_build_options_rejects_flat_payload() -> None:
    args = _make_args()
    with pytest.raises(ValueError, match="nested 'capture'"):
        build_options(
            args=args,
            css_snippets=(),
            js_snippets=(),
            overrides={"max_pages": 5},
        )


def test_build_options_accepts_nested_payload() -> None:
    args = _make_args()
    options = build_options(
        args=args,
        css_snippets=(),
        js_snippets=(),
        overrides={
            "schema_version": "screenshot_options/v2",
            "capture": {"enabled": True, "max_pages": 3},
        },
    )

    assert options.capture.enabled is True
    assert options.capture.max_pages == 3


def test_build_options_merges_css_js_and_extra(tmp_path) -> None:
    args = _make_args()
    css_file = tmp_path / "style.css"
    js_file = tmp_path / "init.js"
    css_file.write_text("body{}", encoding="utf-8")
    js_file.write_text("console.log('hi');", encoding="utf-8")
    args = ScreenshotCliArgs(
        **{
            **args.__dict__,
            "extra_css_paths": (css_file,),
            "extra_js_paths": (js_file,),
        }
    )

    options = build_options(
        args=args,
        css_snippets=("prebuilt { color: red; }",),
        js_snippets=("console.log('a');",),
        overrides={
            "capture": {"enabled": True},
            "browser": {"compatibility_level": "high"},
            "runner": {
                "extra_styles": ["body { font-size: 14px; }"],
                "extra_init_scripts": ["console.log('b');"],
                "extra": {"trace": True},
            },
        },
    )

    assert any("prebuilt" in style for style in options.runner.extra_styles)
    assert any("font-size" in style for style in options.runner.extra_styles)
    assert any("console.log('a')" in script for script in options.runner.extra_init_scripts)
    assert any("console.log('b')" in script for script in options.runner.extra_init_scripts)
    assert options.runner.extra["trace"] is True


def test_build_options_invalid_compatibility_falls_back() -> None:
    args = _make_args()
    options = build_options(
        args=args,
        css_snippets=(),
        js_snippets=(),
        overrides={
            "capture": {"enabled": True},
            "browser": {"compatibility_level": "unsupported-level"},
        },
    )

    assert options.browser.compatibility_level == "high"
