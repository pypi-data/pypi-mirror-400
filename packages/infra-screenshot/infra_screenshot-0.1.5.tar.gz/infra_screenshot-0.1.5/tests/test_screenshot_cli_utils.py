import json
from pathlib import Path
from typing import cast

import pytest

from screenshot import ScreenshotOptions
from screenshot._models_options import (
    OPTIONS_SCHEMA_VERSION,
    BrowserCompatOptions,
    CaptureOptions,
    RunnerOptions,
)
from screenshot.cli_utils import (
    ScreenshotCliArgs,
    ScreenshotJobSpec,
    collect_job_specs,
    derive_job_id,
    serialize_options,
    spec_to_api_payload,
)


def test_collect_job_specs_from_args(tmp_path: Path) -> None:
    cli_args = ScreenshotCliArgs(
        input=None,
        urls=("https://example.com",),
        site_ids=(),
        partition_date="2025-10-21",
        max_pages=3,
        depth=1,
        viewports=("desktop",),
        post_nav_wait_s=0.5,
        timeout_s=45.0,
        max_retries=2,
        job_budget_s=180.0,
        max_viewport_concurrency=None,
    )

    specs = collect_job_specs(cli_args)
    assert len(specs) == 1
    spec: ScreenshotJobSpec = specs[0]
    assert spec["partition_date"] == "2025-10-21"
    assert spec["options"].capture.max_pages == 3
    assert spec["options"].capture.max_total_duration_s == 180.0
    assert spec["options"].browser.allow_autoplay is True
    assert spec["options"].browser.hide_overlays is True
    assert spec["options"].browser.reduced_motion is True
    assert spec["options"].browser.mute_media is True
    assert spec["options"].browser.disable_animations is True
    assert spec["options"].browser.compatibility_level == "high"
    assert spec["options"].capture.max_viewport_concurrency == 1
    assert spec["options"].browser.user_agent is None
    assert spec["metadata"]["source"] == "cli"
    assert spec["metadata"]["backend"] == "playwright"
    assert spec["backend"] == "playwright"
    assert spec["options"].runner.playwright_executable_path is None

    payload: dict[str, object] = spec_to_api_payload(spec)
    assert payload["job_id"]
    options_payload = cast(dict[str, object], payload["options"])
    capture_payload = cast(dict[str, object], options_payload["capture"])
    browser_payload = cast(dict[str, object], options_payload["browser"])
    assert capture_payload["max_pages"] == 3
    assert browser_payload["allow_autoplay"] is True
    assert browser_payload["mute_media"] is True
    assert browser_payload.get("user_agent") is None
    assert capture_payload["max_viewport_concurrency"] == 1
    assert payload["backend"] == "playwright"


def test_collect_job_specs_uses_scroll_tuning_args(tmp_path: Path) -> None:
    cli_args = ScreenshotCliArgs(
        input=None,
        urls=("https://example.com",),
        site_ids=(),
        partition_date="2025-10-21",
        max_pages=1,
        depth=0,
        viewports=("desktop",),
        post_nav_wait_s=0.5,
        timeout_s=45.0,
        max_retries=1,
        job_budget_s=None,
        scroll_step_delay_ms=180,
        max_scroll_steps=7,
        max_viewport_concurrency=None,
    )

    specs = collect_job_specs(cli_args)
    options = specs[0]["options"]

    assert options.capture.scroll_step_delay_ms == 180
    assert options.capture.max_scroll_steps == 7


def test_collect_job_specs_from_json(tmp_path: Path) -> None:
    input_path = tmp_path / "jobs.jsonl"
    input_path.write_text(
        json.dumps(
            {
                "job_id": "marketing-home",
                "url": "https://example.com",
                "partition_date": "2025-10-22",
                "options": {
                    "capture": {
                        "enabled": True,
                        "max_pages": 4,
                        "viewports": ["desktop", "mobile"],
                    },
                    "browser": {},
                    "runner": {},
                },
                "metadata": {"campaign": "launch"},
                "user_agent": "FromFile/1.0",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    cli_args = ScreenshotCliArgs(
        input=input_path,
        urls=(),
        site_ids=(),
        partition_date=None,
        max_pages=5,
        depth=1,
        viewports=("desktop",),
        post_nav_wait_s=0.0,
        timeout_s=60.0,
        max_retries=None,
        job_budget_s=None,
        scroll=False,
        max_viewport_concurrency=None,
    )

    specs = collect_job_specs(cli_args)
    assert len(specs) == 1
    spec: ScreenshotJobSpec = specs[0]
    assert spec["job_id"] == "marketing-home"
    assert spec["options"].capture.max_pages == 4
    assert "mobile" in spec["options"].capture.viewports
    assert spec["options"].browser.allow_autoplay is True
    assert (
        spec["options"].browser.user_agent is None
    )  # legacy top-level user_agent field is ignored
    assert spec["metadata"]["campaign"] == "launch"
    assert spec["metadata"]["backend"] == "playwright"
    assert spec["backend"] == "playwright"


def test_collect_job_specs_from_nested_json(tmp_path: Path) -> None:
    input_path = tmp_path / "jobs_v2.jsonl"
    input_path.write_text(
        json.dumps(
            {
                "job_id": "blog-detail",
                "url": "https://example.com/blog/intro",
                "partition_date": "2025-11-01",
                "options": {
                    "schema_version": OPTIONS_SCHEMA_VERSION,
                    "capture": {
                        "enabled": False,
                        "max_pages": 2,
                        "depth": 2,
                        "viewports": ["mobile"],
                        "post_nav_wait_s": 1.25,
                        "max_total_duration_s": 40.0,
                        "scroll": False,
                        "pre_capture_wait_s": 0.5,
                    },
                    "browser": {
                        "allow_autoplay": False,
                        "hide_overlays": False,
                        "reduced_motion": True,
                        "compatibility_level": "medium",
                        "user_agent": "NestedUA/1.0",
                    },
                    "runner": {
                        "extra_styles": ["body { color: green; }"],
                        "extra_init_scripts": ["console.log('nested');"],
                        "extra": {"locale": "fr-FR"},
                        "playwright_executable_path": "/usr/bin/google-chrome-stable",
                    },
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    cli_args = ScreenshotCliArgs(
        input=input_path,
        urls=(),
        site_ids=(),
        partition_date=None,
        max_pages=5,
        depth=1,
        viewports=("desktop",),
        post_nav_wait_s=0.0,
        timeout_s=45.0,
        max_retries=None,
        job_budget_s=None,
        scroll=True,
        allow_autoplay=True,
        hide_overlays=True,
        reduced_motion=False,
    )

    specs = collect_job_specs(cli_args)
    assert len(specs) == 1
    spec: ScreenshotJobSpec = specs[0]
    options = spec["options"]
    assert spec["backend"] == "playwright"
    assert spec["metadata"]["backend"] == "playwright"
    assert options.capture.enabled is False
    assert options.capture.max_pages == 2
    assert list(options.capture.viewports) == ["mobile"]
    assert options.capture.scroll is False
    assert options.capture.post_nav_wait_s == 1.25
    assert options.capture.max_total_duration_s == 40.0
    assert options.capture.pre_capture_wait_s == 0.5
    assert options.browser.allow_autoplay is False
    assert options.browser.hide_overlays is False
    assert options.browser.compatibility_level == "medium"
    assert options.browser.user_agent == "NestedUA/1.0"
    assert "body { color: green; }" in options.runner.extra_styles
    assert "console.log('nested');" in options.runner.extra_init_scripts
    assert options.runner.extra["locale"] == "fr-FR"
    assert options.runner.playwright_executable_path == "/usr/bin/google-chrome-stable"


def test_collect_job_specs_raises_on_schema_mismatch(tmp_path: Path) -> None:
    input_path = tmp_path / "jobs_invalid_schema.jsonl"
    input_path.write_text(
        json.dumps(
            {
                "job_id": "blog-detail",
                "url": "https://example.com/blog/intro",
                "options": {
                    "schema_version": "screenshot_options/v99",
                    "capture": {"enabled": True},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    cli_args = ScreenshotCliArgs(
        input=input_path,
        urls=(),
        site_ids=(),
        partition_date=None,
        max_pages=5,
        depth=1,
        viewports=("desktop",),
        post_nav_wait_s=0.0,
        timeout_s=60.0,
        max_retries=None,
        job_budget_s=None,
        scroll=False,
        max_viewport_concurrency=None,
    )

    with pytest.raises(ValueError, match="Unsupported screenshot options schema"):
        collect_job_specs(cli_args)


def test_collect_job_specs_boolean_overrides_from_args() -> None:
    cli_args = ScreenshotCliArgs(
        input=None,
        urls=("https://example.com",),
        site_ids=(),
        partition_date=None,
        max_pages=1,
        depth=0,
        viewports=("desktop",),
        post_nav_wait_s=0.0,
        timeout_s=60.0,
        max_retries=None,
        job_budget_s=None,
        allow_autoplay=False,
        hide_overlays=False,
        reduced_motion=True,
        full_page=False,
        pre_capture_wait_s=None,
        max_viewport_concurrency=None,
        override_custom_user_agent="CustomAgent/1.0",
    )

    spec = collect_job_specs(cli_args)[0]
    options = spec["options"]
    assert spec["backend"] == "playwright"
    assert spec["metadata"]["backend"] == "playwright"

    assert options.browser.allow_autoplay is False
    assert options.browser.hide_overlays is False
    assert options.browser.reduced_motion is True
    assert options.capture.full_page is False
    assert options.browser.mute_media is True
    assert options.browser.user_agent == "CustomAgent/1.0"
    assert options.browser.disable_animations is True
    assert options.browser.block_media is False
    assert options.runner.playwright_executable_path is None


def test_collect_job_specs_with_playwright_executable_path(tmp_path: Path) -> None:
    cli_args = ScreenshotCliArgs(
        input=None,
        urls=("https://example.com",),
        site_ids=(),
        partition_date=None,
        max_pages=1,
        depth=0,
        viewports=("desktop",),
        post_nav_wait_s=0.0,
        timeout_s=60.0,
        max_retries=None,
        job_budget_s=None,
        playwright_executable_path="/opt/google/chrome",
    )

    spec = collect_job_specs(cli_args)[0]
    assert spec["options"].runner.playwright_executable_path == "/opt/google/chrome"


def test_collect_job_specs_respects_overrides(tmp_path: Path) -> None:
    input_path = tmp_path / "jobs.jsonl"
    input_path.write_text(
        json.dumps(
            {
                "url": "https://example.com/about",
                "options": {
                    "capture": {
                        "enabled": True,
                        "viewports": ["desktop"],
                        "max_capture_attempts": 5,
                        "max_total_duration_s": 25.0,
                        "max_viewport_concurrency": 2,
                        "full_page": False,
                        "pre_capture_wait_s": 1.5,
                    },
                    "browser": {
                        "allow_autoplay": False,
                        "hide_overlays": False,
                        "reduced_motion": True,
                        "block_media": True,
                        "mute_media": False,
                        "disable_animations": True,
                    },
                    "runner": {
                        "extra_styles": ["body { background: #000; }"],
                        "extra_init_scripts": ["console.log('hi')"],
                        "extra": {"locale": "en-US"},
                    },
                },
                "metadata": ["ignored"],
            }
        )
        + "\n\n"
        + json.dumps({"url": "   "})
        + "\n",
        encoding="utf-8",
    )

    cli_args = ScreenshotCliArgs(
        input=input_path,
        urls=(),
        site_ids=(),
        partition_date="2025-10-23",
        max_pages=5,
        depth=2,
        viewports=("desktop", "mobile"),
        post_nav_wait_s=0.0,
        timeout_s=30.0,
        max_retries=None,
        job_budget_s=120.0,
        max_viewport_concurrency=None,
        allow_autoplay=True,
        hide_overlays=True,
        reduced_motion=False,
        full_page=True,
        pre_capture_wait_s=None,
        chromium_compat="medium",
        override_custom_user_agent="CLI/2.0",
    )

    specs = collect_job_specs(cli_args)
    assert len(specs) == 1
    spec: ScreenshotJobSpec = specs[0]
    options = spec["options"]
    assert spec["backend"] == "playwright"
    assert spec["metadata"]["backend"] == "playwright"
    assert list(options.capture.viewports) == ["desktop"]
    assert options.capture.max_capture_attempts == 5
    assert options.capture.max_total_duration_s == 25.0
    assert options.browser.allow_autoplay is False
    assert options.browser.hide_overlays is False
    assert options.browser.reduced_motion is True
    assert options.capture.full_page is False
    assert options.capture.pre_capture_wait_s == 1.5
    assert options.browser.disable_animations is True
    assert options.browser.block_media is True
    assert options.browser.mute_media is False
    assert options.browser.user_agent == "CLI/2.0"
    assert options.capture.max_viewport_concurrency == 2
    assert "body { background: #000; }" in options.runner.extra_styles
    assert "console.log('hi')" in options.runner.extra_init_scripts
    assert options.runner.extra["locale"] == "en-US"
    assert options.browser.compatibility_level == "medium"
    assert specs[0]["metadata"]["source"] == "cli"


def test_collect_job_specs_uses_arg_level_pre_capture_wait(tmp_path: Path) -> None:
    cli_args = ScreenshotCliArgs(
        input=None,
        urls=("https://example.com/blog",),
        site_ids=(),
        partition_date=None,
        max_pages=2,
        depth=0,
        viewports=("desktop",),
        post_nav_wait_s=0.0,
        timeout_s=40.0,
        max_retries=None,
        job_budget_s=None,
        scroll=False,
        pre_capture_wait_s=3.2,
        max_viewport_concurrency=None,
    )

    specs = collect_job_specs(cli_args)
    spec: ScreenshotJobSpec = specs[0]
    options = spec["options"]
    assert spec["backend"] == "playwright"
    assert spec["metadata"]["backend"] == "playwright"
    assert options.capture.scroll is False
    assert options.capture.pre_capture_wait_s == 3.2
    assert options.browser.mute_media is True
    assert options.browser.user_agent is None


def test_spec_to_api_payload_includes_snapshot() -> None:
    options = ScreenshotOptions(
        capture=CaptureOptions(enabled=True, max_pages=1),
        browser=BrowserCompatOptions(user_agent="SpecUA/1.0"),
    )
    spec: ScreenshotJobSpec = {
        "job_id": "job-1",
        "url": "https://example.com",
        "partition_date": "2025-01-01",
        "metadata": {"source": "cli"},
        "options": options,
        "html_snapshot_path": "/tmp/snapshot.html",
        "backend": "playwright",
    }

    payload: dict[str, object] = spec_to_api_payload(spec)
    options_payload = cast(dict[str, object], payload["options"])
    capture_payload = cast(dict[str, object], options_payload["capture"])
    browser_payload = cast(dict[str, object], options_payload["browser"])
    runner_payload = cast(dict[str, object], options_payload["runner"])

    assert payload["html_snapshot_path"] == "/tmp/snapshot.html"
    assert options_payload["schema_version"] == OPTIONS_SCHEMA_VERSION
    assert capture_payload["enabled"] is True
    assert browser_payload["mute_media"] is True
    assert browser_payload.get("user_agent") == "SpecUA/1.0"
    assert runner_payload.get("playwright_executable_path") is None
    assert payload["backend"] == "playwright"


def test_serialize_options_round_trip() -> None:
    options = ScreenshotOptions(
        capture=CaptureOptions(
            enabled=True,
            max_pages=3,
            depth=2,
            viewports=("desktop", "mobile"),
            post_nav_wait_s=1.0,
            timeout_s=30.0,
            scroll=False,
            max_total_duration_s=120.0,
            max_capture_attempts=4,
            full_page=False,
            pre_capture_wait_s=0.75,
            max_viewport_concurrency=5,
        ),
        browser=BrowserCompatOptions(
            allow_autoplay=False,
            hide_overlays=False,
            reduced_motion=True,
            disable_animations=True,
            mute_media=False,
            block_media=True,
            compatibility_level="high",
            user_agent="UA/3.0",
        ),
        runner=RunnerOptions(
            extra_styles=("body { color: red; }",),
            extra_init_scripts=("console.log('hi')",),
            extra={"foo": "bar"},
        ),
    )

    serialized: dict[str, object] = serialize_options(options)
    capture_payload = cast(dict[str, object], serialized["capture"])
    browser_payload = cast(dict[str, object], serialized["browser"])
    runner_payload = cast(dict[str, object], serialized["runner"])

    assert serialized["schema_version"] == OPTIONS_SCHEMA_VERSION
    assert capture_payload["viewports"] == ["desktop", "mobile"]
    assert capture_payload["max_capture_attempts"] == 4
    assert capture_payload["max_viewport_concurrency"] == 5
    assert browser_payload["mute_media"] is False
    assert browser_payload["disable_animations"] is True
    assert browser_payload["block_media"] is True
    assert browser_payload["compatibility_level"] == "high"
    assert browser_payload["user_agent"] == "UA/3.0"
    assert runner_payload["extra"] == {"foo": "bar"}
    assert "body { color: red; }" in cast(list[str], runner_payload["extra_styles"])
    assert "console.log('hi')" in cast(list[str], runner_payload["extra_init_scripts"])
    assert runner_payload["playwright_executable_path"] is None


def test_collect_job_specs_reads_extra_files(tmp_path: Path) -> None:
    css_path = tmp_path / "extra.css"
    css_path.write_text("body { color: red; }", encoding="utf-8")
    js_path = tmp_path / "extra.js"
    js_path.write_text("console.log('css');", encoding="utf-8")

    cli_args = ScreenshotCliArgs(
        input=None,
        urls=("https://example.com",),
        site_ids=(),
        partition_date=None,
        max_pages=1,
        depth=0,
        viewports=("desktop",),
        post_nav_wait_s=0.0,
        timeout_s=60.0,
        max_retries=None,
        job_budget_s=None,
        scroll=None,
        extra_css_paths=(css_path,),
        extra_js_paths=(js_path,),
        chromium_compat="high",
        max_viewport_concurrency=None,
        override_custom_user_agent="UA/2.0",
    )

    spec = collect_job_specs(cli_args)[0]
    options = spec["options"]
    assert spec["backend"] == "playwright"

    assert "body { color: red; }" in options.runner.extra_styles
    assert "console.log('css');" in options.runner.extra_init_scripts
    assert options.browser.compatibility_level == "high"
    assert options.capture.max_viewport_concurrency == 1
    assert options.browser.user_agent == "UA/2.0"


def test_collect_job_specs_rejects_unsupported_backend() -> None:
    cli_args = ScreenshotCliArgs(
        input=None,
        urls=("https://example.org",),
        site_ids=(),
        partition_date=None,
        max_pages=1,
        depth=0,
        viewports=("desktop",),
        post_nav_wait_s=0.0,
        timeout_s=30.0,
        max_retries=None,
        job_budget_s=None,
        backend="selenium",
    )

    with pytest.raises(ValueError):
        collect_job_specs(cli_args)


def test_derive_job_id_fallback() -> None:
    assert derive_job_id("", fallback="site-1") == "site-1"
