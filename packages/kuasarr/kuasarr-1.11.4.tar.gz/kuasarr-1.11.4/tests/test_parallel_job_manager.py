import asyncio

import pytest

from captcha_helper.service import ParallelJobManager, ParallelJob, PackageInfo, ServiceLogger


def build_package(package_id: str = "pkg1") -> PackageInfo:
    return PackageInfo(
        id=package_id,
        name="Test Package",
        url=[["https://example.com", "example"]],
        mirror=None,
        password="",
        max_attempts=3,
    )


@pytest.mark.asyncio
async def test_enqueue_prevents_duplicates():
    logger = ServiceLogger(level="DEBUG")
    manager = ParallelJobManager(max_concurrent=2, max_queue_size=5, logger=logger)

    package = build_package()
    first_job = ParallelJob(job_id="job-1", package=package)
    second_job = ParallelJob(job_id="job-1", package=package)

    assert await manager.enqueue(first_job) is True
    assert await manager.enqueue(second_job) is False

    metrics = manager.metrics()
    assert metrics["queue_size"] == 1
    assert metrics["total_enqueued"] == 1


@pytest.mark.asyncio
async def test_worker_processes_jobs_and_updates_metrics():
    logger = ServiceLogger(level="DEBUG")
    manager = ParallelJobManager(max_concurrent=1, max_queue_size=2, logger=logger)

    processed = asyncio.Event()

    async def process_callback(job: ParallelJob):
        assert job.job_id == "job-worker"
        processed.set()

    await manager.start(process_callback)

    await manager.enqueue(ParallelJob(job_id="job-worker", package=build_package()))

    await asyncio.wait_for(processed.wait(), timeout=1)

    metrics = manager.metrics()
    assert metrics["queue_size"] == 0
    assert metrics["total_completed"] == 1

    await manager.shutdown()


@pytest.mark.asyncio
async def test_retry_enqueue_when_queue_full():
    logger = ServiceLogger(level="DEBUG")
    manager = ParallelJobManager(max_concurrent=1, max_queue_size=1, logger=logger)

    await manager.enqueue(ParallelJob(job_id="job-a", package=build_package()))
    result = await manager.enqueue(ParallelJob(job_id="job-b", package=build_package("pkg2")))
    assert result is False

    # Manually clear queue to simulate processing
    job = await manager.queue.get()
    manager.queue.task_done()
    manager._known_jobs.discard(job.job_id)

    # Now enqueue should succeed
    assert await manager.enqueue(ParallelJob(job_id="job-b", package=build_package("pkg2")))


@pytest.mark.asyncio
async def test_shutdown_stops_workers_and_clears_queue():
    logger = ServiceLogger(level="DEBUG")
    manager = ParallelJobManager(max_concurrent=2, max_queue_size=3, logger=logger)

    async def noop_callback(job: ParallelJob):
        await asyncio.sleep(0)

    await manager.start(noop_callback)

    await manager.enqueue(ParallelJob(job_id="job-shutdown-1", package=build_package("pkg-shutdown-1")))
    await manager.enqueue(ParallelJob(job_id="job-shutdown-2", package=build_package("pkg-shutdown-2")))

    await manager.shutdown()

    # Queue sollte geleert und keine aktiven Jobs mehr vorhanden sein
    assert manager.queue.empty()
    assert not manager._active_jobs


@pytest.mark.asyncio
async def test_enqueue_rejects_when_job_active():
    logger = ServiceLogger(level="DEBUG")
    manager = ParallelJobManager(max_concurrent=1, max_queue_size=2, logger=logger)

    job = ParallelJob(job_id="job-active", package=build_package())

    # Füge Job hinzu und simuliere aktiven Status
    await manager.enqueue(job)
    manager._active_jobs[job.job_id] = job

    duplicate = ParallelJob(job_id="job-active", package=build_package())
    assert await manager.enqueue(duplicate) is False

    manager._active_jobs.pop(job.job_id)
