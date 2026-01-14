"""Job/result/resource dataclasses used across the screenshot package."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from ._shared.errors import ScreenshotError

if TYPE_CHECKING:
    from ._models_options import ScreenshotOptions


@runtime_checkable
class CancellationToken(Protocol):
    def raise_if_cancelled(self) -> None: ...


@dataclass
class ScreenshotJob:
    job_id: str
    url: str
    output_root: Path
    options: ScreenshotOptions
    partition_date: str | None = None
    html_snapshot_path: Path | None = None
    cancel_token: CancellationToken | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class ScreenshotCaptureResult:
    requested: int
    captured: int
    failed: int
    metadata_path: Path | None
    entries: list[dict[str, object]] = field(default_factory=list)
    errors: list[ScreenshotError] = field(default_factory=list)
    job_id: str | None = None

    @property
    def succeeded(self) -> bool:
        return not self.errors and (self.requested == 0 or self.captured > 0)

    @property
    def error_messages(self) -> list[str]:
        return [error.message for error in self.errors]

    def add_error(self, error: ScreenshotError) -> None:
        self.errors.append(error)


class ScreenshotResourceOutcome(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class ScreenshotResourceError:
    category: str
    message: str
    retryable: bool
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category,
            "message": self.message,
            "retryable": self.retryable,
            "details": dict(self.details),
        }


@dataclass
class ScreenshotResourceResult:
    resource_key: str
    outcome: ScreenshotResourceOutcome
    config_key: str
    errors: list[ScreenshotResourceError] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)
    entries: list[dict[str, object]] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "resource_key": self.resource_key,
            "outcome": self.outcome.value,
            "config_key": self.config_key,
            "errors": [error.to_dict() for error in self.errors],
            "metadata": dict(self.metadata),
        }


@dataclass
class ScreenshotViewportResource:
    resource_key: str
    viewport: str
    outcome: ScreenshotResourceOutcome
    config_key: str
    errors: list[ScreenshotResourceError]
    metadata: dict[str, object]


@dataclass
class ScreenshotBatchResult:
    results: list[ScreenshotCaptureResult]

    @property
    def failures(self) -> list[ScreenshotCaptureResult]:
        return [result for result in self.results if not result.succeeded]

    @property
    def successes(self) -> list[ScreenshotCaptureResult]:
        return [result for result in self.results if result.succeeded]

    def to_dict(self) -> dict[str, object]:
        return {
            "results": [
                {
                    "job_id": result.job_id,
                    "requested": result.requested,
                    "captured": result.captured,
                    "failed": result.failed,
                    "metadata_path": str(result.metadata_path) if result.metadata_path else None,
                    "errors": [error.to_dict() for error in result.errors],
                }
                for result in self.results
            ],
            "success_count": len(self.successes),
            "failure_count": len(self.failures),
        }

    @classmethod
    def from_results(cls, results: Iterable[ScreenshotCaptureResult]) -> ScreenshotBatchResult:
        return cls(results=list(results))
