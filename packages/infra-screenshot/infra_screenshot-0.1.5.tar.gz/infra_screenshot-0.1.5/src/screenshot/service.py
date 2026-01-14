"""Async-first orchestration helpers for screenshot batches.

The `ScreenshotService` wraps a backend implementation and coordinates
concurrency, cancellation, and aggregation of `ScreenshotCaptureResult`
objects. It is primarily used by CLIs and worker processes that want a
consistent interface regardless of the underlying runner.

Example:
    >>> import asyncio
    >>> from pathlib import Path
    >>> from screenshot.cli import PlaywrightScreenshotBackend
    >>> service = ScreenshotService(backend=PlaywrightScreenshotBackend(), concurrency=2)
    >>> jobs = [ScreenshotJob(job_id="demo", url="https://example.com", output_root=Path("/tmp"))]
    >>> batch = asyncio.run(service.capture_async(jobs))
    >>> batch.successes[0].captured
    1
"""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
from typing import Generic, Protocol, TypeVar, cast, runtime_checkable

from ._shared.errors import make_error
from .models import ScreenshotBatchResult, ScreenshotCaptureResult, ScreenshotJob

TResult = TypeVar("TResult", bound=ScreenshotCaptureResult)
TResult_co = TypeVar("TResult_co", bound=ScreenshotCaptureResult, covariant=True)


@runtime_checkable
class CancelToken(Protocol):
    """Protocol describing the cancel token hook used by runners."""

    def raise_if_cancelled(self) -> None: ...


@runtime_checkable
class ScreenshotBackend(Protocol, Generic[TResult_co]):
    """Backend interface responsible for executing individual screenshot jobs."""

    async def run_job_async(self, job: ScreenshotJob) -> TResult_co: ...


class ScreenshotService(Generic[TResult]):
    """High-level helper that executes batches of screenshot jobs."""

    def __init__(self, backend: ScreenshotBackend[TResult], *, concurrency: int = 1) -> None:
        if concurrency <= 0:
            raise ValueError("concurrency must be positive")
        self._backend = backend
        self._default_concurrency = concurrency

    async def capture_async(
        self,
        jobs: Iterable[ScreenshotJob],
        *,
        concurrency: int | None = None,
        cancel_token: CancelToken | None = None,
    ) -> ScreenshotBatchResult:
        """Execute the provided jobs asynchronously with optional overrides.

        Args:
            jobs: Iterable of screenshot jobs to process.
            concurrency: Optional override for the maximum in-flight jobs.
            cancel_token: Cooperative cancellation token exposing `raise_if_cancelled`.

        Returns:
            Aggregated `ScreenshotBatchResult` summarizing successes/failures.

        Example:
            >>> import asyncio
            >>> from pathlib import Path
            >>> async def _demo():
            ...     backend = PlaywrightScreenshotBackend()  # doctest: +SKIP
            ...     service = ScreenshotService(backend, concurrency=2)  # doctest: +SKIP
            ...     jobs = [
            ...         ScreenshotJob(
            ...             job_id="demo",
            ...             url="https://example.com",
            ...             output_root=Path("/tmp"),
            ...         )
            ...     ]  # doctest: +SKIP
            ...     return await service.capture_async(jobs)  # doctest: +SKIP
            >>> # asyncio.run(_demo())  # doctest: +SKIP
        """

        job_list: list[ScreenshotJob] = list(jobs)
        if not job_list:
            return ScreenshotBatchResult(results=[])

        limit = concurrency or self._default_concurrency
        semaphore = asyncio.Semaphore(limit)
        results: list[TResult] = []

        async def _run(job: ScreenshotJob) -> None:
            if cancel_token is not None:
                cancel_token.raise_if_cancelled()
            async with semaphore:
                try:
                    result = await self._backend.run_job_async(job)
                except asyncio.CancelledError:
                    raise
                except Exception as exc:  # pragma: no cover - defensive
                    error_result = ScreenshotCaptureResult(
                        requested=1,
                        captured=0,
                        failed=1,
                        metadata_path=None,
                        entries=[],
                        errors=[
                            make_error(
                                "backend",
                                f"Screenshot job failed: {exc}",
                                retryable=True,
                                details={"job_id": job.job_id},
                            )
                        ],
                        job_id=job.job_id,
                    )
                    results.append(cast(TResult, error_result))
                else:
                    if result.job_id is None:
                        result.job_id = job.job_id
                    results.append(result)

        await asyncio.gather(*(_run(job) for job in job_list))
        return ScreenshotBatchResult.from_results(results)

    def capture(
        self,
        jobs: Iterable[ScreenshotJob],
        *,
        concurrency: int | None = None,
    ) -> ScreenshotBatchResult:
        """Synchronous wrapper around `capture_async` for CLI scripts.

        This helper spins up a dedicated event loop via `asyncio.run`, so it
        should only be used from non-async contexts such as entry points or
        small scripts. Call `capture_async` when integrating into async code.

        Example:
            >>> service = ScreenshotService(backend=...)  # doctest: +SKIP
            >>> service.capture([])  # doctest: +SKIP
            ScreenshotBatchResult(results=[])
        """

        return asyncio.run(self.capture_async(jobs, concurrency=concurrency))
