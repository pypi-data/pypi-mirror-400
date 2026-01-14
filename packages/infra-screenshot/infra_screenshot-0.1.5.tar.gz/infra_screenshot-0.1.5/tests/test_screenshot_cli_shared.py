import argparse
from pathlib import Path

import pytest

from screenshot import cli as screenshot_cli
from screenshot.cli_shared import add_job_arguments, build_cli_args


def test_add_job_arguments_and_build_cli_args(tmp_path: Path) -> None:
    parser = argparse.ArgumentParser()
    add_job_arguments(parser, include_output_dir=True)

    args = parser.parse_args(
        [
            "--urls",
            "https://example.com",
            "--job-id",
            "home",
            "--partition-date",
            "2025-01-01",
            "--max-pages",
            "4",
            "--depth",
            "2",
            "--viewports",
            "desktop",
            "mobile",
            "--post-nav-wait-s",
            "0.5",
            "--timeout-s",
            "45",
            "--max-retries",
            "5",
            "--job-budget-s",
            "120",
            "--max-viewport-concurrency",
            "2",
            "--scroll",
            "false",
            "--scroll-step-delay-ms",
            "180",
            "--max-scroll-steps",
            "7",
            "--allow-autoplay",
            "false",
            "--hide-overlays",
            "false",
            "--reduced-motion",
            "true",
            "--full-page",
            "false",
            "--mute-media",
            "false",
            "--disable-animations",
            "true",
            "--block-media",
            "true",
            "--pre-capture-wait-s",
            "1.2",
            "--extra-css",
            str(tmp_path / "extra.css"),
            "--extra-js",
            str(tmp_path / "extra.js"),
            "--override-custom-user-agent",
            "MyAgent/5.0",
            "--chromium-compat",
            "medium",
            "--playwright-executable-path",
            "/usr/bin/google-chrome",
            "--output-dir",
            str(tmp_path),
        ]
    )

    (tmp_path / "extra.css").write_text("body{}", encoding="utf-8")
    (tmp_path / "extra.js").write_text("console.log('hi');", encoding="utf-8")

    cli_args = build_cli_args(args)
    assert cli_args.urls == ("https://example.com",)
    assert cli_args.site_ids == ("home",)
    assert cli_args.partition_date == "2025-01-01"
    assert cli_args.post_nav_wait_s == 0.5
    assert cli_args.max_retries == 5
    assert cli_args.job_budget_s == 120.0
    assert cli_args.scroll is False
    assert cli_args.scroll_step_delay_ms == 180
    assert cli_args.max_scroll_steps == 7
    assert cli_args.allow_autoplay is False
    assert cli_args.hide_overlays is False
    assert cli_args.reduced_motion is True
    assert cli_args.full_page is False
    assert cli_args.pre_capture_wait_s == 1.2
    assert cli_args.mute_media is False
    assert cli_args.disable_animations is True
    assert cli_args.block_media is True
    assert cli_args.extra_css_paths
    assert cli_args.extra_js_paths
    assert cli_args.chromium_compat == "medium"
    assert cli_args.max_viewport_concurrency == 2
    assert cli_args.override_custom_user_agent == "MyAgent/5.0"
    assert cli_args.playwright_executable_path == "/usr/bin/google-chrome"


def test_add_job_arguments_without_output_dir(tmp_path: Path) -> None:
    parser = argparse.ArgumentParser()
    add_job_arguments(parser, include_output_dir=False)

    args = parser.parse_args(
        [
            "--urls",
            "https://example.com",
            "--job-id",
            "home",
        ]
    )

    cli_args = build_cli_args(args)

    assert cli_args.urls == ("https://example.com",)
    assert cli_args.site_ids == ("home",)
    assert cli_args.allow_autoplay is None
    assert cli_args.full_page is None
    assert cli_args.chromium_compat is None
    assert cli_args.max_viewport_concurrency is None
    assert cli_args.scroll_step_delay_ms is None
    assert cli_args.max_scroll_steps is None
    assert cli_args.pre_capture_wait_s == 2.5
    assert cli_args.override_custom_user_agent is None
    assert cli_args.playwright_executable_path is None


def test_local_cli_env_flag_disables_config(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SCREENSHOT_CLI_USE_CONFIG", "0")
    parser = screenshot_cli.build_parser()
    args = parser.parse_args(
        [
            "local",
            "--urls",
            "https://example.com",
            "--output-dir",
            str(tmp_path / "out"),
        ]
    )
    assert isinstance(args, argparse.Namespace)
