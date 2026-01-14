from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from screenshot._shared.storage import dumps_json


class FakeEnum(Enum):
    VALUE = "value"


def test_dumps_json_handles_paths_and_enums(tmp_path: Path) -> None:
    data = {
        "path": tmp_path / "file.txt",
        "timestamp": datetime(2025, 1, 1, tzinfo=UTC),
        "enum": FakeEnum.VALUE,
    }

    serialized = dumps_json(data)
    assert '"path"' in serialized
    assert str(tmp_path / "file.txt") in serialized
    assert "value" in serialized
    assert serialized.endswith("\n")
