from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from screenshot import (
    ScreenshotBatchResult,
    ScreenshotCaptureResult,
    ScreenshotJob,
    ScreenshotOptions,
    ScreenshotService,
)
from screenshot._shared.errors import make_error
from screenshot.models import CaptureOptions


class RecordingBackend:
    def __init__(self) -> None:
        self.jobs: list[ScreenshotJob] = []

    async def run_job_async(self, job: ScreenshotJob) -> ScreenshotCaptureResult:
        self.jobs.append(job)
        return ScreenshotCaptureResult(
            requested=1,
            captured=1,
            failed=0,
            metadata_path=None,
            entries=[],
            errors=[],
            job_id=job.job_id,
        )


@pytest.mark.asyncio
async def test_screenshot_service_capture_async(tmp_path: Path) -> None:
    backend = RecordingBackend()
    service = ScreenshotService(backend, concurrency=2)
    jobs = [
        ScreenshotJob(
            job_id=f"job-{index}",
            url=f"https://example.com/{index}",
            output_root=tmp_path,
            options=ScreenshotOptions(capture=CaptureOptions(enabled=True)),
        )
        for index in range(3)
    ]

    result = await service.capture_async(jobs)

    assert isinstance(result, ScreenshotBatchResult)
    assert len(result.results) == 3
    assert len(result.failures) == 0
    assert [job.job_id for job in backend.jobs] == [job.job_id for job in jobs]


def test_screenshot_service_capture_sync(tmp_path: Path) -> None:
    backend = RecordingBackend()
    service = ScreenshotService(backend, concurrency=1)
    job = ScreenshotJob(
        job_id="sync",
        url="https://example.com",
        output_root=tmp_path,
        options=ScreenshotOptions(capture=CaptureOptions(enabled=True)),
    )

    result = service.capture([job])

    assert len(result.results) == 1
    assert result.results[0].job_id == "sync"
    assert backend.jobs[0].job_id == "sync"


def test_screenshot_service_requires_positive_concurrency() -> None:
    backend = RecordingBackend()
    with pytest.raises(ValueError):
        ScreenshotService(backend, concurrency=0)


class NullJobIdBackend:
    def __init__(self) -> None:
        self.jobs: list[ScreenshotJob] = []

    async def run_job_async(self, job: ScreenshotJob) -> ScreenshotCaptureResult:
        self.jobs.append(job)
        return ScreenshotCaptureResult(
            requested=1,
            captured=0,
            failed=1,
            metadata_path=None,
            entries=[],
            errors=[make_error("runtime", "failed")],
            job_id=None,
        )


@pytest.mark.asyncio
async def test_screenshot_service_backfills_job_id(tmp_path: Path) -> None:
    backend = NullJobIdBackend()
    service = ScreenshotService(backend, concurrency=2)
    job = ScreenshotJob(
        job_id="job-123",
        url="https://example.com",
        output_root=tmp_path,
        options=ScreenshotOptions(capture=CaptureOptions(enabled=True)),
    )

    result = await service.capture_async([job])

    assert result.results[0].job_id == "job-123"
    assert backend.jobs[0].job_id == "job-123"


@pytest.mark.asyncio
async def test_screenshot_service_checks_cancel_token(tmp_path: Path) -> None:
    class CountingToken:
        def __init__(self) -> None:
            self.calls = 0

        def raise_if_cancelled(self) -> None:
            self.calls += 1

    token = CountingToken()
    backend = RecordingBackend()
    service = ScreenshotService(backend, concurrency=1)
    jobs = [
        ScreenshotJob(
            job_id=f"job-{index}",
            url=f"https://example.com/{index}",
            output_root=tmp_path,
            options=ScreenshotOptions(capture=CaptureOptions(enabled=True)),
        )
        for index in range(2)
    ]

    await service.capture_async(jobs, cancel_token=token)

    assert token.calls == len(jobs)


@pytest.mark.asyncio
async def test_screenshot_service_handles_no_jobs() -> None:
    backend = RecordingBackend()
    service = ScreenshotService(backend, concurrency=1)

    result = await service.capture_async([])

    assert result.results == []


class FailingBackend:
    async def run_job_async(self, job: ScreenshotJob) -> ScreenshotCaptureResult:
        raise RuntimeError(f"boom-{job.job_id}")


@pytest.mark.asyncio
async def test_screenshot_service_converts_backend_error(tmp_path: Path) -> None:
    backend = FailingBackend()
    service = ScreenshotService(backend, concurrency=1)
    job = ScreenshotJob(
        job_id="err",
        url="https://example.com",
        output_root=tmp_path,
        options=ScreenshotOptions(capture=CaptureOptions(enabled=True)),
    )

    result = await service.capture_async([job])

    assert len(result.results) == 1
    failure = result.results[0]
    assert failure.job_id == "err"
    assert failure.failed == 1
    assert failure.errors and "boom-err" in failure.errors[0].message


class CancelledBackend:
    async def run_job_async(
        self, job: ScreenshotJob
    ) -> ScreenshotCaptureResult:  # pragma: no cover
        raise asyncio.CancelledError()


@pytest.mark.asyncio
async def test_screenshot_service_propagates_cancel(tmp_path: Path) -> None:
    backend = CancelledBackend()
    service = ScreenshotService(backend, concurrency=1)
    job = ScreenshotJob(
        job_id="cancel",
        url="https://example.com",
        output_root=tmp_path,
        options=ScreenshotOptions(capture=CaptureOptions(enabled=True)),
    )

    with pytest.raises(asyncio.CancelledError):
        await service.capture_async([job])
