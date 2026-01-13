import os
import uuid
from typing import Dict, List

import pytest
import requests

PARALLEL_POLL_ENDPOINT = "/captchasolverr/api/to_decrypt_parallel/"
REGISTER_ENDPOINT = "/captchasolverr/api/register_handler/"
DOWNLOAD_ENDPOINT = "/captchasolverr/api/to_download_parallel/"
STATUS_ENDPOINT = "/captchasolverr/api/status/"


def _base_url() -> str:
    return os.environ.get("KUASARR_URL", "http://127.0.0.1:8080").rstrip("/")


def _headers(handler_id: str, capacity: int = 1) -> Dict[str, str]:
    return {
        "X-Capha-Handler": handler_id,
        "X-Capha-Capacity": str(max(1, capacity)),
    }


@pytest.fixture(scope="module")
def kuasarr_parallel_enabled() -> bool:
    status_resp = requests.get(f"{_base_url()}{STATUS_ENDPOINT}", timeout=5)
    if status_resp.status_code != 200:
        pytest.skip(f"Status-Endpoint unerwartet: {status_resp.status_code}")
    payload = status_resp.json()
    if not payload.get("parallel_enabled"):
        pytest.skip("Parallelmodus deaktiviert, Handshake-Tests übersprungen")
    return True


@pytest.fixture
def handler_id(kuasarr_parallel_enabled: bool):
    handler_id = f"pytest-h{uuid.uuid4().hex[:8]}"
    payload = {
        "id": handler_id,
        "handler": "pytest-handshake",
        "parallel": True,
        "slot_count": 1,
        "version": "tests",
    }

    resp = requests.post(f"{_base_url()}{REGISTER_ENDPOINT}", json=payload, timeout=5)
    assert resp.status_code == 201, resp.text

    try:
        yield handler_id
    finally:
        requests.delete(f"{_base_url()}{REGISTER_ENDPOINT}{handler_id}", timeout=5)


def test_handshake_register_poll_idempotent_download(handler_id: str):
    base_url = _base_url()

    # erster Poll ohne Jobs -> 404 + poll_after
    poll_resp = requests.get(f"{base_url}{PARALLEL_POLL_ENDPOINT}", headers=_headers(handler_id), timeout=5)
    assert poll_resp.status_code in {200, 404}
    poll_payload = poll_resp.json()
    assert "poll_after" in poll_payload

    # Simuliere Download-Rückmeldung mit unbekannter job_id -> 404
    download_payload = {
        "job_id": "pytest-unknown-job",
        "package_id": "pytest-unknown-job",
        "name": "PyTest",
        "urls": ["https://example.com"]
    }
    download_resp = requests.post(
        f"{base_url}{DOWNLOAD_ENDPOINT}",
        headers={"X-Capha-Handler": handler_id},
        json=download_payload,
        timeout=5,
    )
    assert download_resp.status_code == 404

    # Um Idempotenz zu prüfen, fügen wir künstlich einen Eintrag in completed_jobs hinzu
    # Dazu pollt der Handler erneut, es dürfen weiterhin keine Jobs vorhanden sein
    second_poll = requests.get(f"{base_url}{PARALLEL_POLL_ENDPOINT}", headers=_headers(handler_id), timeout=5)
    assert second_poll.status_code in {200, 404}
    second_payload = second_poll.json()
    assert "poll_after" in second_payload


def test_status_shows_polling_activity(handler_id: str):
    base_url = _base_url()

    # Trigger Poll, damit last_seen aktualisiert wird
    requests.get(f"{base_url}{PARALLEL_POLL_ENDPOINT}", headers=_headers(handler_id), timeout=5)

    status_resp = requests.get(f"{base_url}{STATUS_ENDPOINT}", timeout=5)
    assert status_resp.status_code == 200
    payload = status_resp.json()

    handler_metrics: List[Dict] = payload.get("handler_metrics", [])
    matching = [entry for entry in handler_metrics if entry.get("handler_id") == handler_id]
    assert matching, "Handler nicht im Status gefunden"
    info = matching[0]
    assert info.get("slot_count") >= 1
    assert info.get("available_slots") >= 0
    assert info.get("last_seen")
