"""Storage abstractions shared within the screenshot package."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@lru_cache(maxsize=1)
def _ensure_parent_impl() -> Callable[[Path], None]:
    from infra_core.fs_utils import ensure_parent as infra_ensure_parent

    return infra_ensure_parent


def _ensure_parent(path: Path) -> None:
    _ensure_parent_impl()(path)


def _default_json_serializer(value: object) -> Any:
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except TypeError:
            pass
    if isinstance(value, Enum):
        return value.value
    return value


@runtime_checkable
class StorageBackend(Protocol):
    """Writable storage interface for screenshot artifacts."""

    def ensure_parent(self, path: Path) -> None: ...

    def write_json(self, path: Path, data: dict[str, Any]) -> Path: ...

    def write_text(self, path: Path, text: str) -> Path: ...


@runtime_checkable
class CloudStorageBackend(StorageBackend, Protocol):
    """Extension for backends that support synchronous uploads."""

    def upload_file(self, path: Path) -> None: ...


@runtime_checkable
class AsyncStorageBackend(StorageBackend, Protocol):
    """Extension for backends that expose true async uploads."""

    async def upload_file_async(self, path: Path) -> None: ...


class LocalStorageBackend:
    """Default storage backend that only writes to the local filesystem."""

    def ensure_parent(self, path: Path) -> None:
        _ensure_parent(path)

    def write_json(self, path: Path, data: dict[str, Any]) -> Path:
        self.ensure_parent(path)
        path.write_text(dumps_json(data), encoding="utf-8")
        return path

    async def write_json_async(self, path: Path, data: dict[str, Any]) -> Path:
        return await asyncio.to_thread(self.write_json, path, data)

    def write_text(self, path: Path, text: str) -> Path:
        self.ensure_parent(path)
        path.write_text(text, encoding="utf-8")
        return path

    async def write_text_async(self, path: Path, text: str) -> Path:
        return await asyncio.to_thread(self.write_text, path, text)

    def upload_file(self, path: Path) -> None:  # pragma: no cover - no-op default
        return None


def dumps_json(data: dict[str, Any]) -> str:
    """Serialize data to JSON with stable formatting and Path/Enum awareness."""

    import json

    text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        default=_default_json_serializer,
    )
    return f"{text}\n"
