from __future__ import annotations

import json
from pathlib import Path

import pytest

from screenshot import (
    ScreenshotBatchResult,
    ScreenshotCaptureResult,
    ScreenshotOptions,
    cli as screenshot_cli,
)


class _FakeService:
    def __init__(self, batch: ScreenshotBatchResult) -> None:
        self._batch = batch

    def capture(self, jobs):  # type: ignore[override]
        return self._batch


def test_cmd_local_writes_summary(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    summary_file = tmp_path / "out" / "summary.json"

    success = ScreenshotCaptureResult(
        requested=1,
        captured=1,
        failed=0,
        metadata_path=None,
        entries=[],
        errors=[],
        job_id="job-1",
    )
    batch = ScreenshotBatchResult(results=[success])

    monkeypatch.setattr(
        screenshot_cli,
        "collect_job_specs",
        lambda args: [
            {
                "job_id": "job-1",
                "url": "https://example.com",
                "partition_date": None,
                "html_snapshot_path": None,
                "metadata": {},
                "options": ScreenshotOptions(),
                "backend": "playwright",
            }
        ],
    )
    monkeypatch.setattr(
        screenshot_cli,
        "build_local_screenshot_service",
        lambda concurrency=1, backend="playwright", storage=None: _FakeService(batch),
    )

    parser = screenshot_cli.build_parser()
    args = parser.parse_args(
        [
            "local",
            "--urls",
            "https://example.com",
            "--output-dir",
            str(tmp_path / "out"),
            "--summary-file",
            str(summary_file),
        ]
    )

    exit_code = screenshot_cli._cmd_local(args)

    assert exit_code == 0
    assert summary_file.exists()
    payload = json.loads(summary_file.read_text(encoding="utf-8"))
    assert payload["success_count"] == 1
