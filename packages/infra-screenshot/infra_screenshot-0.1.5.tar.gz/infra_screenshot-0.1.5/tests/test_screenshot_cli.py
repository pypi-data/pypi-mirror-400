import argparse
import json
from pathlib import Path

import pytest

from screenshot import (
    ScreenshotBatchResult,
    ScreenshotCaptureResult,
    ScreenshotJob,
    ScreenshotOptions,
)
from screenshot._models_options import OPTIONS_SCHEMA_VERSION, CaptureOptions
from screenshot._shared.errors import make_error
from screenshot.cli import (
    PlaywrightScreenshotBackend,
    SeleniumScreenshotBackend,
    _cmd_local,
    build_local_screenshot_service,
    main as cli_main,
)


class DummyService:
    def __init__(self, result: ScreenshotBatchResult) -> None:
        self._result = result
        self.calls = 0
        self.jobs = None

    def capture(self, jobs):
        self.calls += 1
        self.jobs = list(jobs)
        return self._result


def _build_args(tmp_path: Path, **overrides) -> argparse.Namespace:
    defaults = {
        "input": None,
        "urls": (),
        "site_ids": (),
        "partition_date": None,
        "max_pages": 5,
        "depth": 1,
        "viewports": ("desktop",),
        "post_nav_wait_s": 0.0,
        "timeout_s": 60.0,
        "max_retries": None,
        "job_budget_s": None,
        "scroll": None,
        "allow_autoplay": None,
        "hide_overlays": None,
        "reduced_motion": None,
        "full_page": None,
        "pre_capture_wait_s": None,
        "mute_media": None,
        "disable_animations": None,
        "block_media": None,
        "chromium_compat": None,
        "extra_css": None,
        "extra_js": None,
        "output_dir": tmp_path / "output",
        "site_concurrency": 1,
        "summary_file": None,
        "backend": "playwright",
        "playwright_executable_path": None,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_cmd_local_writes_summary_and_calls_service(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    spec = {
        "job_id": "marketing-home",
        "url": "https://example.com",
        "partition_date": "2024-11-01",
        "html_snapshot_path": None,
        "metadata": {"source": "cli", "backend": "playwright"},
        "options": ScreenshotOptions(capture=CaptureOptions(enabled=True, max_pages=2)),
        "backend": "playwright",
    }
    batch_result = ScreenshotBatchResult(
        results=[
            ScreenshotCaptureResult(
                requested=1,
                captured=1,
                failed=0,
                metadata_path=None,
                entries=[{"job_id": "marketing-home"}],
                errors=[],
                job_id="marketing-home",
            )
        ]
    )
    dummy_service = DummyService(batch_result)
    summary_path = tmp_path / "summary.json"

    monkeypatch.setattr("screenshot.cli.collect_job_specs", lambda _: [spec])

    def _build_service(**kwargs):
        assert kwargs.get("backend") == "playwright"
        return dummy_service

    monkeypatch.setattr("screenshot.cli.build_local_screenshot_service", _build_service)

    args = _build_args(tmp_path, summary_file=summary_path)

    exit_code = _cmd_local(args)

    assert exit_code == 0
    assert dummy_service.calls == 1
    assert dummy_service.jobs and dummy_service.jobs[0].job_id == "marketing-home"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["success_count"] == 1
    assert summary["failure_count"] == 0


def test_cmd_local_handles_missing_jobs(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    caplog.set_level("ERROR")
    monkeypatch.setattr("screenshot.cli.collect_job_specs", lambda _: [])
    monkeypatch.setattr(
        "screenshot.cli.build_local_screenshot_service",
        lambda **_: pytest.fail("should not build service"),
    )

    args = _build_args(tmp_path)

    exit_code = _cmd_local(args)

    assert exit_code == 1
    assert "No screenshot jobs specified" in caplog.text


def test_cmd_local_file_not_found(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    caplog.set_level("ERROR")

    def raise_not_found(_):
        raise FileNotFoundError("jobs.jsonl")

    monkeypatch.setattr("screenshot.cli.collect_job_specs", raise_not_found)
    monkeypatch.setattr(
        "screenshot.cli.build_local_screenshot_service",
        lambda **_: pytest.fail("should not build service"),
    )

    args = _build_args(tmp_path, input=tmp_path / "missing.jsonl")

    exit_code = _cmd_local(args)

    assert exit_code == 1
    assert "Input file" in caplog.text


def test_cmd_local_json_error(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    caplog.set_level("ERROR")

    def raise_json_error(_):
        raise json.JSONDecodeError("bad json", "{}", 0)

    monkeypatch.setattr("screenshot.cli.collect_job_specs", raise_json_error)
    monkeypatch.setattr(
        "screenshot.cli.build_local_screenshot_service",
        lambda **_: pytest.fail("should not build service"),
    )

    args = _build_args(tmp_path, input=tmp_path / "invalid.jsonl")

    exit_code = _cmd_local(args)

    assert exit_code == 1
    assert "Failed to parse" in caplog.text


def test_cmd_local_logs_failed_jobs(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    caplog.set_level("INFO")
    spec = {
        "job_id": "marketing-home",
        "url": "https://example.com",
        "partition_date": None,
        "html_snapshot_path": None,
        "metadata": {"source": "cli", "backend": "playwright"},
        "options": ScreenshotOptions(capture=CaptureOptions(enabled=True)),
        "backend": "playwright",
    }
    batch_result = ScreenshotBatchResult(
        results=[
            ScreenshotCaptureResult(
                requested=1,
                captured=0,
                failed=1,
                metadata_path=None,
                entries=[],
                errors=[make_error("runtime", "boom")],
                job_id="marketing-home",
            )
        ]
    )
    dummy_service = DummyService(batch_result)

    monkeypatch.setattr("screenshot.cli.collect_job_specs", lambda _: [spec])
    monkeypatch.setattr("screenshot.cli.build_local_screenshot_service", lambda **_: dummy_service)

    args = _build_args(tmp_path)

    exit_code = _cmd_local(args)

    assert exit_code == 1
    assert "failed: boom" in caplog.text


def test_cli_local_integration_with_json_input(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    input_path = tmp_path / "jobs.jsonl"
    input_path.write_text(
        json.dumps(
            {
                "job_id": "integration-case",
                "url": "https://example.com",
                "partition_date": "2025-12-01",
                "options": {
                    "schema_version": OPTIONS_SCHEMA_VERSION,
                    "capture": {
                        "enabled": True,
                        "max_pages": 2,
                        "viewports": ["desktop", "mobile"],
                    },
                    "browser": {"allow_autoplay": False, "compatibility_level": "medium"},
                },
                "metadata": {"source": "jsonl"},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    summary_path = tmp_path / "summary.json"
    output_dir = tmp_path / "output"

    metadata_path = output_dir / "integration-case" / "metadata" / "screenshots.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps({"entries": [{"screenshot_path": "shot.png", "status": "success"}]}),
        encoding="utf-8",
    )

    capture_result = ScreenshotCaptureResult(
        requested=1,
        captured=1,
        failed=0,
        metadata_path=metadata_path,
        entries=[
            {
                "job_id": "integration-case",
                "url": "https://example.com",
                "status": "success",
                "screenshot_path": str(
                    metadata_path.parent.parent / "assets" / "screenshots" / "shot.png"
                ),
                "error": None,
            }
        ],
        errors=[],
        job_id="integration-case",
    )
    batch_result = ScreenshotBatchResult(results=[capture_result])

    class StubService:
        def __init__(self, result: ScreenshotBatchResult) -> None:
            self.result = result
            self.calls = 0
            self.jobs: list[ScreenshotJob] | None = None

        def capture(self, jobs):
            self.calls += 1
            self.jobs = list(jobs)
            return self.result

    stub_service = StubService(batch_result)
    monkeypatch.setattr("screenshot.cli.build_local_screenshot_service", lambda **_: stub_service)

    exit_code = cli_main(
        [
            "local",
            "--input",
            str(input_path),
            "--output-dir",
            str(output_dir),
            "--summary-file",
            str(summary_path),
            "--backend",
            "playwright",
        ]
    )

    assert exit_code == 0
    assert stub_service.calls == 1
    assert stub_service.jobs is not None
    job = stub_service.jobs[0]
    assert job.job_id == "integration-case"
    assert list(job.options.capture.viewports) == ["desktop", "mobile"]
    assert job.options.capture.max_pages == 2
    assert summary_path.exists()
    summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary_payload["success_count"] == 1
    assert summary_payload["failure_count"] == 0


@pytest.mark.asyncio
async def test_playwright_backend_runs_job(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured = {}

    async def fake_capture_async(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return ScreenshotCaptureResult(
            requested=1,
            captured=1,
            failed=0,
            metadata_path=None,
            entries=[],
            errors=[],
            job_id=None,
        )

    monkeypatch.setattr("screenshot.cli.playwright_capture_async", fake_capture_async)
    storage = object()
    backend = PlaywrightScreenshotBackend(storage=storage)
    job = ScreenshotJob(
        job_id="job-1",
        url="https://example.com",
        output_root=tmp_path,
        options=ScreenshotOptions(capture=CaptureOptions(enabled=True)),
    )

    result = await backend.run_job_async(job)

    assert captured["kwargs"]["storage"] is storage
    assert result.job_id == "job-1"


def test_build_local_screenshot_service_clamps_concurrency() -> None:
    service = build_local_screenshot_service(concurrency=0)
    assert service._default_concurrency == 1


def test_build_local_screenshot_service_selects_backends() -> None:
    service_playwright = build_local_screenshot_service(concurrency=1, backend="playwright")
    assert isinstance(service_playwright._backend, PlaywrightScreenshotBackend)

    service_selenium = build_local_screenshot_service(concurrency=1, backend="selenium")
    assert isinstance(service_selenium._backend, SeleniumScreenshotBackend)


def test_cmd_local_rejects_mixed_backends(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    caplog.set_level("ERROR")
    spec_a = {
        "job_id": "site-a",
        "url": "https://example.com",
        "partition_date": None,
        "html_snapshot_path": None,
        "metadata": {"source": "cli", "backend": "playwright"},
        "options": ScreenshotOptions(capture=CaptureOptions(enabled=True)),
        "backend": "playwright",
    }
    spec_b = {
        "job_id": "site-b",
        "url": "https://example.org",
        "partition_date": None,
        "html_snapshot_path": None,
        "metadata": {"source": "cli", "backend": "selenium"},
        "options": ScreenshotOptions(capture=CaptureOptions(enabled=True)),
        "backend": "selenium",
    }

    monkeypatch.setattr("screenshot.cli.collect_job_specs", lambda _: [spec_a, spec_b])

    args = _build_args(tmp_path)
    exit_code = _cmd_local(args)
    assert exit_code == 1
    assert "Mixed backend selections" in caplog.text


def test_main_invokes_cmd_local(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    called = {}

    def fake_cmd_local(args: argparse.Namespace) -> int:
        called["args"] = args
        return 0

    monkeypatch.setattr("screenshot.cli._cmd_local", fake_cmd_local)

    exit_code = cli_main(
        [
            "--verbose",
            "local",
            "--output-dir",
            str(tmp_path / "output"),
            "--urls",
            "https://example.com",
        ]
    )

    assert exit_code == 0
    assert called["args"].verbose is True


def test_main_unknown_command_exits() -> None:
    with pytest.raises(SystemExit):
        cli_main(["unknown"])
