from __future__ import annotations

from screenshot._shared.cli.normalizers import (
    _bool_field,
    _ensure_list,
    _numeric_field,
    _pick,
    _to_float,
)


def test_ensure_list_and_pick() -> None:
    containers = [{"first": None}, {"second": "two"}, "not-a-dict"]  # type: ignore[list-item]

    assert _ensure_list(None) == []
    assert _ensure_list("single") == ["single"]
    assert sorted(_ensure_list({"a", "b"})) == ["a", "b"]
    assert _pick(containers, "first", "second") == "two"
    assert _pick(containers, "missing") is None


def test_to_float_and_bool_field() -> None:
    containers = [{"flag": False}, {"flag": True}]

    assert _to_float("not-a-number", 1.5) == 1.5
    assert _to_float(3, 0.0) == 3.0
    # Container value wins over CLI arg and default
    assert _bool_field(containers, ["flag"], arg_value=True, default=True) is False
    # With no container hit, fall back to CLI arg then default
    assert _bool_field([{}], ["flag"], arg_value=None, default=True) is True


def test_numeric_field_prefers_container_and_enforces_minimum() -> None:
    containers = [{"depth": "5"}]

    value = _numeric_field(
        containers,
        ["depth"],
        fallback=None,
        default=2.0,
        coerce=float,
        minimum=1.0,
    )
    assert value == 5.0

    clamped = _numeric_field(
        [{}],
        ["missing"],
        fallback="-3",
        default=2.0,
        coerce=float,
        minimum=0.0,
    )
    assert clamped == 0.0
