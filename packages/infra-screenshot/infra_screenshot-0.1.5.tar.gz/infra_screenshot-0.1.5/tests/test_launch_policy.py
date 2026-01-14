import pytest

from screenshot.launch_policy import build_chromium_args, describe_levels, normalise_level


def test_normalise_level_accepts_known_values() -> None:
    assert normalise_level(" HIGH ") == "high"
    assert normalise_level("medium") == "medium"
    with pytest.raises(ValueError):
        normalise_level("extreme")


def test_build_chromium_args_removes_duplicates_and_respects_overrides() -> None:
    flags = build_chromium_args(
        "medium",
        extra_args=["--custom-flag", "--disable-gpu"],
        skip_args=["--disable-gpu"],
    )
    assert "--allow-running-insecure-content" in flags  # medium-level flag
    assert "--disable-gpu" not in flags  # explicitly skipped
    assert flags.count("--custom-flag") == 1


def test_describe_levels_returns_expected_ordering() -> None:
    levels = describe_levels()
    assert set(levels.keys()) == {"low", "medium", "high"}
    assert len(levels["medium"]) > len(levels["low"])
