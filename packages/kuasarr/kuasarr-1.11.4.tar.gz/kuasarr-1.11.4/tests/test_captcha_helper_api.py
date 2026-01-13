import asyncio
import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def handler_module(tmp_path):
    from captcha_helper import captcha_handler as handler

    handler = importlib.reload(handler)

    db_path = tmp_path / "async_jobs.db"
    handler.job_store = handler.AsyncJobStore(db_path)
    handler.job_registry = handler.AsyncJobRegistry(handler.job_store)
    handler.async_job_queue = asyncio.Queue()
    handler.async_job_workers = []
    handler.async_worker_target = 1
    handler._async_runtime_ready = False
    handler._async_runtime_lock = asyncio.Lock()

    config = handler.CaptchaConfig(
        deathbycaptcha_token="token",
        nox_user="",
        nox_pass="",
    )
    app = handler.create_app(config)
    client = TestClient(app)
    return handler, client


def test_solve_sync_success(handler_module, monkeypatch):
    handler, client = handler_module

    async def fake_process_external_payload(raw_payload, job_id=None):
        return handler.ProcessingResult.SUCCESS, handler.DecryptionResponse(
            status=200,
            urls=["https://example.com"],
            mirror="Example",
        )

    monkeypatch.setattr(handler.engine, "process_external_payload", fake_process_external_payload)

    response = client.post(
        "/solve",
        json={
            "captcha_type": "captchasolverr",
            "mode": "sync",
            "payload": {"links": [["https://filecrypt.test", "filecrypt"]]},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "finished"
    assert data["result"]["urls"] == ["https://example.com"]
    assert data["result"]["mirror"] == "Example"


def test_solve_async_creates_job(handler_module, monkeypatch):
    handler, client = handler_module

    async def fake_ready():
        handler._async_runtime_ready = True

    monkeypatch.setattr(handler, "_ensure_async_runtime_ready", fake_ready)

    response = client.post(
        "/solve",
        json={
            "captcha_type": "captchasolverr",
            "mode": "async",
            "payload": {"links": [["https://filecrypt.test", "filecrypt"]]},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"

    job = asyncio.run(handler.job_registry.get_job(data["job_id"]))
    assert job is not None
    assert job.status == handler.JobStatus.QUEUED

    asyncio.run(handler.job_registry.remove_job(job.job_id))


def test_callback_updates_job(handler_module):
    handler, client = handler_module

    async def create_job():
        return await handler.job_registry.create_job(
            "job-callback",
            "captchasolverr",
            {"payload": {}},
            None,
            180,
        )

    asyncio.run(create_job())

    response = client.post(
        "/callback",
        json={
            "job_id": "job-callback",
            "status": "finished",
            "result": {
                "job_id": "job-callback",
                "urls": ["https://example.com/result"],
                "mirror": "Rapidgator",
                "replace_url": None,
                "session": None,
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "finished"

    job = asyncio.run(handler.job_registry.get_job("job-callback"))
    assert job is not None
    assert job.status == handler.JobStatus.FINISHED
    assert job.result["urls"] == ["https://example.com/result"]

    asyncio.run(handler.job_registry.remove_job("job-callback"))
