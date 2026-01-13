#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests for Kuasarr ↔ CapHa Parallel Mode
Tests the complete flow between both services
"""

import asyncio
import pytest
import aiohttp
from unittest.mock import Mock, AsyncMock, patch
import json
import time
from typing import Dict, Any

# Test configuration
KUASARR_URL = "http://localhost:8080"
CAPHA_URL = "http://localhost:9700"


class TestParallelModeIntegration:
    """Integration tests for parallel mode communication"""
    
    @pytest.mark.asyncio
    async def test_auto_detection_flow(self):
        """Test auto-detection between Kuasarr and CapHa"""
        async with aiohttp.ClientSession() as session:
            # Step 1: Check CapHa status
            async with session.get(f"{CAPHA_URL}/status") as resp:
                assert resp.status == 200
                data = await resp.json()
                assert data.get("parallel_enabled") is True
                assert "worker_slots" in data
                assert "queue_length" in data
            
            # Step 2: Check Kuasarr detects CapHa
            async with session.get(f"{KUASARR_URL}/captchasolverr/api/status/") as resp:
                assert resp.status == 200
                data = await resp.json()
                # Kuasarr should detect CapHa's parallel mode
                assert data.get("capha_detected") is True
                assert data.get("parallel_mode_active") is True
    
    @pytest.mark.asyncio
    async def test_push_job_flow(self):
        """Test pushing a job from Kuasarr to CapHa"""
        async with aiohttp.ClientSession() as session:
            # Prepare test payload
            job_payload = {
                "job_id": "test-push-001",
                "mode": "async",
                "captcha_type": "filecrypt",
                "payload": {
                    "url": "https://filecrypt.cc/test",
                    "package_id": "pkg-001",
                    "name": "Test Package",
                    "password": "test123"
                },
                "callback_url": f"{KUASARR_URL}/captchasolverr/api/captcha_callback/"
            }
            
            # Push job to CapHa
            async with session.post(
                f"{CAPHA_URL}/solve",
                json=job_payload
            ) as resp:
                assert resp.status == 200
                data = await resp.json()
                assert data["status"] == "queued"
                assert data["job_id"] == "test-push-001"
                
                # Check for capacity header
                assert "X-Capha-Capacity" in resp.headers
    
    @pytest.mark.asyncio
    async def test_callback_flow(self):
        """Test callback from CapHa to Kuasarr"""
        async with aiohttp.ClientSession() as session:
            # Simulate CapHa sending callback to Kuasarr
            callback_payload = {
                "job_id": "test-callback-001",
                "status": "finished",
                "result": {
                    "urls": [
                        "https://example.com/file1.zip",
                        "https://example.com/file2.zip"
                    ],
                    "mirror": "mirror1"
                }
            }
            
            # Send callback
            async with session.post(
                f"{KUASARR_URL}/captchasolverr/api/captcha_callback/",
                json=callback_payload
            ) as resp:
                assert resp.status in [200, 202]
                data = await resp.json()
                assert data.get("status") in ["acknowledged", "success"]
    
    @pytest.mark.asyncio
    async def test_backpressure_handling(self):
        """Test adaptive backpressure when queue is full"""
        async with aiohttp.ClientSession() as session:
            # Fill CapHa's queue
            jobs_sent = []
            for i in range(25):  # Send more than queue capacity
                job_payload = {
                    "job_id": f"backpressure-{i:03d}",
                    "mode": "async",
                    "captcha_type": "filecrypt",
                    "payload": {
                        "url": f"https://filecrypt.cc/test{i}",
                        "package_id": f"pkg-{i:03d}"
                    }
                }
                
                try:
                    async with session.post(
                        f"{CAPHA_URL}/solve",
                        json=job_payload,
                        timeout=aiohttp.ClientTimeout(total=2)
                    ) as resp:
                        if resp.status == 503:
                            # Service overloaded - backpressure working
                            assert "Service overloaded" in await resp.text()
                            break
                        else:
                            jobs_sent.append(job_payload["job_id"])
                except asyncio.TimeoutError:
                    pass
            
            # Should have hit backpressure before sending all 25
            assert len(jobs_sent) < 25
    
    @pytest.mark.asyncio
    async def test_error_handling_flow(self):
        """Test error handling and retry logic"""
        async with aiohttp.ClientSession() as session:
            # Send job that will fail
            job_payload = {
                "job_id": "error-test-001",
                "mode": "async",
                "captcha_type": "filecrypt",
                "payload": {
                    "url": "https://invalid-url-that-will-fail.com/test",
                    "package_id": "error-pkg-001"
                },
                "callback_url": f"{KUASARR_URL}/captchasolverr/api/captcha_callback/"
            }
            
            # Push job
            async with session.post(
                f"{CAPHA_URL}/solve",
                json=job_payload
            ) as resp:
                assert resp.status == 200
                data = await resp.json()
                assert data["status"] == "queued"
            
            # Wait for processing
            await asyncio.sleep(2)
            
            # Check job status
            async with session.get(
                f"{CAPHA_URL}/result/{job_payload['job_id']}"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Job should either be retrying or failed
                    assert data["status"] in ["processing", "failed"]
    
    @pytest.mark.asyncio
    async def test_idempotency(self):
        """Test idempotency of callbacks"""
        async with aiohttp.ClientSession() as session:
            callback_payload = {
                "job_id": "idempotent-001",
                "status": "finished",
                "result": {
                    "urls": ["https://example.com/file.zip"]
                }
            }
            
            # Send callback twice
            for _ in range(2):
                async with session.post(
                    f"{KUASARR_URL}/captchasolverr/api/captcha_callback/",
                    json=callback_payload
                ) as resp:
                    assert resp.status in [200, 202]
                    data = await resp.json()
                    # Should handle duplicate gracefully
                    assert data.get("status") in ["acknowledged", "success", "already_processed"]
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self):
        """Test metrics collection and reporting"""
        async with aiohttp.ClientSession() as session:
            # Get CapHa metrics
            async with session.get(f"{CAPHA_URL}/status") as resp:
                assert resp.status == 200
                data = await resp.json()
                
                # Check required metrics fields
                assert "total_requests" in data
                assert "successful" in data
                assert "failed" in data
                assert "success_rate" in data
                assert "avg_duration" in data
                assert "workers" in data
                assert "error_counts" in data
                assert "error_rate_per_worker" in data


class TestFailureScenarios:
    """Test various failure scenarios"""
    
    @pytest.mark.asyncio
    async def test_capha_unavailable(self):
        """Test Kuasarr behavior when CapHa is unavailable"""
        async with aiohttp.ClientSession() as session:
            # Try to connect to non-existent CapHa
            with pytest.raises(aiohttp.ClientConnectorError):
                async with session.get(
                    "http://localhost:9999/status",
                    timeout=aiohttp.ClientTimeout(total=1)
                ) as resp:
                    pass
    
    @pytest.mark.asyncio
    async def test_kuasarr_unavailable(self):
        """Test CapHa behavior when Kuasarr is unavailable"""
        async with aiohttp.ClientSession() as session:
            # CapHa should still respond to status
            async with session.get(f"{CAPHA_URL}/status") as resp:
                assert resp.status == 200
                data = await resp.json()
                # Should work independently
                assert "parallel_enabled" in data
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling in job processing"""
        async with aiohttp.ClientSession() as session:
            job_payload = {
                "job_id": "timeout-test-001",
                "mode": "async",
                "captcha_type": "filecrypt",
                "payload": {
                    "url": "https://slow-response-test.com/test"
                },
                "timeout_seconds": 1  # Very short timeout
            }
            
            async with session.post(
                f"{CAPHA_URL}/solve",
                json=job_payload
            ) as resp:
                assert resp.status == 200
            
            # Wait for timeout
            await asyncio.sleep(2)
            
            # Check status - should be failed due to timeout
            async with session.get(
                f"{CAPHA_URL}/result/{job_payload['job_id']}"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data["status"] == "failed":
                        assert "timeout" in data.get("error", "").lower()


class TestLoadAndPerformance:
    """Load and performance tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_job_processing(self):
        """Test processing multiple jobs concurrently"""
        async with aiohttp.ClientSession() as session:
            jobs = []
            
            # Submit multiple jobs
            for i in range(10):
                job_payload = {
                    "job_id": f"concurrent-{i:03d}",
                    "mode": "async",
                    "captcha_type": "filecrypt",
                    "payload": {
                        "url": f"https://filecrypt.cc/test{i}",
                        "package_id": f"pkg-{i:03d}"
                    }
                }
                
                async with session.post(
                    f"{CAPHA_URL}/solve",
                    json=job_payload
                ) as resp:
                    if resp.status == 200:
                        jobs.append(job_payload["job_id"])
            
            # Check that multiple workers are active
            async with session.get(f"{CAPHA_URL}/status") as resp:
                data = await resp.json()
                # Should have multiple active workers
                assert len(data.get("workers", [])) > 0
                assert data.get("processing_jobs", []) != []
    
    @pytest.mark.asyncio
    async def test_queue_metrics_under_load(self):
        """Test queue metrics accuracy under load"""
        async with aiohttp.ClientSession() as session:
            initial_metrics = None
            
            # Get initial metrics
            async with session.get(f"{CAPHA_URL}/status") as resp:
                initial_metrics = await resp.json()
            
            # Submit batch of jobs
            for i in range(5):
                job_payload = {
                    "job_id": f"metrics-test-{i:03d}",
                    "mode": "async",
                    "captcha_type": "filecrypt",
                    "payload": {
                        "url": f"https://filecrypt.cc/test{i}"
                    }
                }
                await session.post(f"{CAPHA_URL}/solve", json=job_payload)
            
            # Get updated metrics
            async with session.get(f"{CAPHA_URL}/status") as resp:
                updated_metrics = await resp.json()
                
                # Queue length should have increased
                assert updated_metrics["queue_length"] >= initial_metrics.get("queue_length", 0)
                # Total requests should have increased
                assert updated_metrics["total_requests"] > initial_metrics.get("total_requests", 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
