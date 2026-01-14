import argparse
from pathlib import Path

import pytest

from screenshot import cli as screenshot_cli, cli_shared
from screenshot.cli_config import apply_config_to_parser, load_cli_config


def _option_strings(parser: argparse.ArgumentParser) -> set[tuple[str, ...]]:
    opts = set()
    for action in parser._actions:
        if action.option_strings:
            opts.add(tuple(sorted(action.option_strings)))
    return opts


def test_config_matches_programmatic_args(tmp_path: Path) -> None:
    programmatic = argparse.ArgumentParser()
    cli_shared.add_job_arguments(programmatic, include_output_dir=True)

    config_parser = argparse.ArgumentParser()
    cli_shared.add_job_arguments(config_parser, include_output_dir=True, use_config=True)

    assert _option_strings(programmatic) == _option_strings(config_parser)


def test_load_cli_config_custom_path(tmp_path: Path) -> None:
    custom_yaml = tmp_path / "cli.yaml"
    custom_yaml.write_text(
        """
        {
          "version": "0.0.1",
          "metadata": {"package": "screenshot"},
          "arguments": {
            "urls": {
              "flags": ["--urls"],
              "type": "str"
            }
          }
        }
        """,
        encoding="utf-8",
    )
    config = load_cli_config(custom_yaml)
    assert config.version == "0.0.1"
    assert "urls" in config.arguments


def test_apply_config_preset_excludes_advanced() -> None:
    config = load_cli_config()
    parser = argparse.ArgumentParser()
    apply_config_to_parser(parser, config, preset="azure_service")

    options = {opt for action in parser._actions for opt in action.option_strings}
    assert "--extra-css" not in options
    assert "--url" in options or "--urls" in options


def test_missing_config_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_cli_config(tmp_path / "missing.yaml")


def test_screenshot_cli_respects_config_flag(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SCREENSHOT_CLI_USE_CONFIG", "1")
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
    assert args.urls == ["https://example.com"]
