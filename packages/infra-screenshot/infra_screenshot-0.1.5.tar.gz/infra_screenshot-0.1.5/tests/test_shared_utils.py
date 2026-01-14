from __future__ import annotations

import json
from pathlib import Path

from screenshot._shared.storage import LocalStorageBackend, dumps_json
from screenshot._shared.url import normalize_url


def test_normalize_url_basic_canonicalization() -> None:
    assert normalize_url("HTTP://Example.com///foo/") == "http://example.com/foo"


def test_normalize_url_drops_fragment_and_default_ports() -> None:
    result = normalize_url("https://example.com:443/path?x=1#section")
    assert result == "https://example.com/path?x=1"


def test_local_storage_backend_roundtrip(tmp_path: Path) -> None:
    backend = LocalStorageBackend()
    target = tmp_path / "data" / "item.json"

    payload = {"job_id": "site", "status": "success"}
    backend.write_json(target, payload)

    assert target.exists()
    assert json.loads(target.read_text(encoding="utf-8")) == payload

    text_target = tmp_path / "data" / "note.txt"
    backend.write_text(text_target, "hello")
    assert text_target.read_text(encoding="utf-8") == "hello"


def test_dumps_json_matches_backend(tmp_path: Path) -> None:
    backend = LocalStorageBackend()
    data = {"value": 1}
    text = dumps_json(data)
    target = tmp_path / "out.json"
    backend.ensure_parent(target)
    target.write_text(text, encoding="utf-8")
    assert json.loads(target.read_text(encoding="utf-8")) == data
