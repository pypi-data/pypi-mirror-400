#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Parallel Queue/Worker System
Tests the ParallelJobManager, Queue handling, and Worker lifecycle
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
import time
from typing import Dict, Any

# Import the components to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from captcha_helper.service import ParallelJob, ParallelJobManager, ServiceLogger


class TestParallelJobManager:
    """Test suite for ParallelJobManager"""
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger"""
        logger = Mock(spec=ServiceLogger)
        logger.info = Mock()
        logger.warning = Mock()
        logger.error = Mock()
        logger.debug = Mock()
        return logger
    
    @pytest.fixture
    async def job_manager(self, mock_logger):
        """Create a ParallelJobManager instance"""
        manager = ParallelJobManager(
            max_concurrent=3,
            max_queue_size=10,
            logger=mock_logger
        )
        yield manager
        # Cleanup
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_enqueue_job(self, job_manager):
        """Test enqueueing a job"""
        job = ParallelJob(
            job_id="test-001",
            package={"id": "pkg-001", "name": "Test Package"},
            attempts=0,
            max_attempts=3
        )
        
        result = await job_manager.enqueue(job)
        assert result is True
        assert job.job_id in job_manager._known_jobs
        assert job_manager.queue.qsize() == 1
    
    @pytest.mark.asyncio
    async def test_enqueue_duplicate_job(self, job_manager):
        """Test that duplicate jobs are rejected"""
        job = ParallelJob(
            job_id="test-002",
            package={"id": "pkg-002", "name": "Test Package"},
            attempts=0,
            max_attempts=3
        )
        
        # First enqueue should succeed
        result1 = await job_manager.enqueue(job)
        assert result1 is True
        
        # Second enqueue with same job_id should fail
        result2 = await job_manager.enqueue(job)
        assert result2 is False
        assert job_manager.queue.qsize() == 1
    
    @pytest.mark.asyncio
    async def test_queue_overflow(self, job_manager):
        """Test queue overflow handling"""
        # Fill the queue to capacity
        for i in range(10):
            job = ParallelJob(
                job_id=f"test-{i:03d}",
                package={"id": f"pkg-{i:03d}", "name": f"Package {i}"},
                attempts=0,
                max_attempts=3
            )
            await job_manager.enqueue(job)
        
        # Queue should be full
        assert job_manager.queue.full()
        
        # Try to add one more - should raise or timeout
        overflow_job = ParallelJob(
            job_id="overflow",
            package={"id": "overflow", "name": "Overflow"},
            attempts=0,
            max_attempts=3
        )
        
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(job_manager.enqueue(overflow_job), timeout=0.1)
    
    @pytest.mark.asyncio
    async def test_worker_processing(self, job_manager, mock_logger):
        """Test worker processing of jobs"""
        processed_jobs = []
        
        async def mock_processor(job):
            processed_jobs.append(job.job_id)
            await asyncio.sleep(0.1)  # Simulate processing
        
        job_manager.set_processor(mock_processor)
        await job_manager.start_workers()
        
        # Add some jobs
        for i in range(5):
            job = ParallelJob(
                job_id=f"worker-test-{i}",
                package={"id": f"pkg-{i}", "name": f"Package {i}"},
                attempts=0,
                max_attempts=3
            )
            await job_manager.enqueue(job)
        
        # Wait for processing
        await asyncio.sleep(0.5)
        
        # Check that jobs were processed
        assert len(processed_jobs) > 0
        assert "worker-test-0" in processed_jobs
    
    @pytest.mark.asyncio
    async def test_schedule_retry(self, job_manager):
        """Test retry scheduling with backoff"""
        job = ParallelJob(
            job_id="retry-test",
            package={"id": "pkg-retry", "name": "Retry Package"},
            attempts=1,
            max_attempts=3
        )
        
        start_time = time.time()
        result = await job_manager.schedule_retry(job, delay_seconds=1)
        assert result is True
        
        # Job should not be in queue immediately
        assert job_manager.queue.qsize() == 0
        
        # Wait for retry delay
        await asyncio.sleep(1.1)
        
        # Job should now be in queue
        assert job_manager.queue.qsize() == 1
        elapsed = time.time() - start_time
        assert elapsed >= 1.0
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown(self, job_manager):
        """Test graceful shutdown of workers"""
        processing_count = {"count": 0}
        
        async def slow_processor(job):
            processing_count["count"] += 1
            await asyncio.sleep(2)  # Slow processing
        
        job_manager.set_processor(slow_processor)
        await job_manager.start_workers()
        
        # Add a job
        job = ParallelJob(
            job_id="shutdown-test",
            package={"id": "pkg-shutdown", "name": "Shutdown Package"},
            attempts=0,
            max_attempts=3
        )
        await job_manager.enqueue(job)
        
        # Start shutdown immediately
        await asyncio.sleep(0.1)  # Let worker pick up the job
        shutdown_task = asyncio.create_task(job_manager.shutdown())
        
        # Shutdown should wait for job to complete
        await shutdown_task
        
        # Job should have been processed
        assert processing_count["count"] == 1
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, job_manager):
        """Test metrics collection"""
        # Process some jobs
        async def quick_processor(job):
            if "fail" in job.job_id:
                raise Exception("Test failure")
        
        job_manager.set_processor(quick_processor)
        await job_manager.start_workers()
        
        # Add mix of successful and failing jobs
        for i in range(3):
            job = ParallelJob(
                job_id=f"success-{i}",
                package={"id": f"pkg-{i}", "name": f"Package {i}"},
                attempts=0,
                max_attempts=1
            )
            await job_manager.enqueue(job)
        
        for i in range(2):
            job = ParallelJob(
                job_id=f"fail-{i}",
                package={"id": f"fail-{i}", "name": f"Fail Package {i}"},
                attempts=0,
                max_attempts=1
            )
            await job_manager.enqueue(job)
        
        # Wait for processing
        await asyncio.sleep(0.5)
        
        # Get metrics
        metrics = job_manager.metrics()
        
        assert metrics["queue_size"] == 0  # All processed
        assert metrics["active_workers"] <= 3
        assert metrics["total_processed"] >= 5
    
    @pytest.mark.asyncio
    async def test_concurrent_worker_limit(self, job_manager):
        """Test that concurrent worker limit is respected"""
        active_workers = {"count": 0, "max": 0}
        
        async def counting_processor(job):
            active_workers["count"] += 1
            active_workers["max"] = max(active_workers["max"], active_workers["count"])
            await asyncio.sleep(0.2)
            active_workers["count"] -= 1
        
        job_manager.set_processor(counting_processor)
        await job_manager.start_workers()
        
        # Add more jobs than workers
        for i in range(10):
            job = ParallelJob(
                job_id=f"concurrent-{i}",
                package={"id": f"pkg-{i}", "name": f"Package {i}"},
                attempts=0,
                max_attempts=3
            )
            await job_manager.enqueue(job)
        
        # Wait for processing
        await asyncio.sleep(1)
        
        # Max concurrent should not exceed limit
        assert active_workers["max"] <= 3


class TestParallelJob:
    """Test suite for ParallelJob"""
    
    def test_job_creation(self):
        """Test creating a ParallelJob"""
        job = ParallelJob(
            job_id="test-job",
            package={"id": "pkg-001", "name": "Test Package"},
            attempts=0,
            max_attempts=3
        )
        
        assert job.job_id == "test-job"
        assert job.package["id"] == "pkg-001"
        assert job.attempts == 0
        assert job.max_attempts == 3
    
    def test_job_retry_increment(self):
        """Test retry attempt increment"""
        job = ParallelJob(
            job_id="retry-job",
            package={"id": "pkg-001", "name": "Test Package"},
            attempts=0,
            max_attempts=3
        )
        
        # Create retry job
        retry_job = ParallelJob(
            job_id=job.job_id,
            package=job.package,
            attempts=job.attempts + 1,
            max_attempts=job.max_attempts
        )
        
        assert retry_job.attempts == 1
        assert retry_job.max_attempts == 3
    
    def test_job_max_attempts_reached(self):
        """Test checking if max attempts reached"""
        job = ParallelJob(
            job_id="max-attempts",
            package={"id": "pkg-001", "name": "Test Package"},
            attempts=2,
            max_attempts=3
        )
        
        assert job.attempts < job.max_attempts
        
        # After another attempt
        job.attempts += 1
        assert job.attempts >= job.max_attempts


class TestQueueBehavior:
    """Test queue-specific behaviors"""
    
    @pytest.mark.asyncio
    async def test_fifo_ordering(self):
        """Test that queue maintains FIFO order"""
        queue = asyncio.Queue(maxsize=10)
        
        # Add jobs in order
        for i in range(5):
            job = ParallelJob(
                job_id=f"fifo-{i}",
                package={"id": f"pkg-{i}", "name": f"Package {i}"},
                attempts=0,
                max_attempts=3
            )
            await queue.put(job)
        
        # Retrieve jobs - should be in same order
        retrieved = []
        while not queue.empty():
            job = await queue.get()
            retrieved.append(job.job_id)
        
        assert retrieved == [f"fifo-{i}" for i in range(5)]
    
    @pytest.mark.asyncio
    async def test_queue_blocking_behavior(self):
        """Test queue blocking when full"""
        queue = asyncio.Queue(maxsize=2)
        
        # Fill queue
        for i in range(2):
            job = ParallelJob(
                job_id=f"block-{i}",
                package={"id": f"pkg-{i}", "name": f"Package {i}"},
                attempts=0,
                max_attempts=3
            )
            await queue.put(job)
        
        # Queue is now full
        assert queue.full()
        
        # Try to add another - should block
        blocked_job = ParallelJob(
            job_id="blocked",
            package={"id": "blocked", "name": "Blocked"},
            attempts=0,
            max_attempts=3
        )
        
        put_task = asyncio.create_task(queue.put(blocked_job))
        await asyncio.sleep(0.1)
        
        # Task should still be pending
        assert not put_task.done()
        
        # Remove one item
        await queue.get()
        
        # Now put should complete
        await put_task
        assert queue.qsize() == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
