from unittest.mock import AsyncMock

import pytest

from captcha_helper.service import (
    DecryptionResponse,
    ParallelJob,
    ProcessingEngine,
    ServiceConfig,
    PackageInfo,
)


def build_engine() -> ProcessingEngine:
    config = ServiceConfig(
        kuasarr_url="http://localhost:8080",
        captcha_handler_url="http://127.0.0.1:9700",
        poll_interval=1,
        parallel_mode=True,
        max_concurrent=1,
        max_queue_size=2,
        parallel_poll_interval=1,
        parallel_retry_backoff=1,
    )
    return ProcessingEngine(config)


def build_job(job_id: str = "job-1", attempts: int = 1, max_attempts: int = 2) -> ParallelJob:
    package = PackageInfo(
        id="pkg-1",
        name="Pkg",
        url=[["https://example.com", "example"]],
        mirror=None,
        password="",
        max_attempts=max_attempts,
    )
    return ParallelJob(job_id=job_id, package=package, attempts=attempts, max_attempts=max_attempts)


@pytest.mark.asyncio
async def test_process_parallel_job_success_sends_result():
    engine = build_engine()
    engine.parallel_handler_id = "handler-1"

    engine.captcha_api.decrypt_payload = AsyncMock(return_value=DecryptionResponse(status=200, urls=["http://dl"]))
    engine.kuasarr_api.send_parallel_result = AsyncMock()
    engine.kuasarr_api.mark_package_failed = AsyncMock()

    await engine._process_parallel_job(build_job())

    engine.kuasarr_api.send_parallel_result.assert_awaited_once()
    engine.kuasarr_api.mark_package_failed.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_parallel_job_requeues_on_retry():
    engine = build_engine()
    engine.parallel_handler_id = "handler-2"

    engine.captcha_api.decrypt_payload = AsyncMock(return_value=DecryptionResponse(status=500, urls=[]))
    engine.kuasarr_api.send_parallel_result = AsyncMock()
    engine.kuasarr_api.mark_package_failed = AsyncMock()

    class DummyManager:
        def __init__(self):
            self.enqueued = []

        async def enqueue(self, job: ParallelJob) -> bool:
            self.enqueued.append(job)
            return True

    dummy_manager = DummyManager()
    engine.job_manager = dummy_manager

    await engine._process_parallel_job(build_job(job_id="job-retry", attempts=1, max_attempts=2))

    assert len(dummy_manager.enqueued) == 1
    retry_job = dummy_manager.enqueued[0]
    assert retry_job.attempts == 2
    engine.kuasarr_api.send_parallel_result.assert_not_awaited()
    engine.kuasarr_api.mark_package_failed.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_parallel_job_marks_failed_after_max_attempts():
    engine = build_engine()
    engine.parallel_handler_id = "handler-3"

    engine.captcha_api.decrypt_payload = AsyncMock(return_value=DecryptionResponse(status=500, urls=[]))
    engine.kuasarr_api.send_parallel_result = AsyncMock()
    engine.kuasarr_api.mark_package_failed = AsyncMock()

    engine.job_manager = None

    await engine._process_parallel_job(build_job(job_id="job-fail", attempts=2, max_attempts=2))

    engine.kuasarr_api.send_parallel_result.assert_not_awaited()
    engine.kuasarr_api.mark_package_failed.assert_awaited_once()
