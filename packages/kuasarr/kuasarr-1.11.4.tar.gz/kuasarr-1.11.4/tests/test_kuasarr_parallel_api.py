import os
import uuid
from typing import Dict

import pytest
import requests


PARALLEL_POLL_ENDPOINT = "/captchasolverr/api/to_decrypt_parallel/"
REGISTER_ENDPOINT = "/captchasolverr/api/register_handler/"
STATUS_ENDPOINT = "/captchasolverr/api/status/"


def _base_url_from_env() -> str:
    url = os.environ.get("KUASARR_URL", "http://127.0.0.1:8080")
    return url.rstrip("/")


@pytest.fixture(scope="module")
def kuasarr_base_url() -> str:
    return _base_url_from_env()


@pytest.fixture(scope="module")
def kuasarr_status(kuasarr_base_url: str) -> Dict:
    try:
        response = requests.get(f"{kuasarr_base_url}{STATUS_ENDPOINT}", timeout=5)
    except requests.ConnectionError as exc:
        pytest.skip(f"Kuasarr nicht erreichbar: {exc}")
    if response.status_code != 200:
        pytest.skip(f"Status-Endpoint unerwartet: {response.status_code} {response.text}")

    data = response.json()
    if not data.get("parallel_enabled"):
        pytest.skip("Parallelmodus ist deaktiviert – Tests werden übersprungen")
    return data


@pytest.fixture
def registered_handler(kuasarr_base_url: str, kuasarr_status: Dict) -> str:
    handler_id = f"pytest-{uuid.uuid4().hex[:10]}"
    payload = {
        "id": handler_id,
        "handler": "pytest",
        "parallel": True,
        "slot_count": 2,
        "version": "test-suite",
    }

    response = requests.post(
        f"{kuasarr_base_url}{REGISTER_ENDPOINT}",
        json=payload,
        timeout=5,
    )
    assert response.status_code == 201, response.text

    try:
        yield handler_id
    finally:
        requests.delete(
            f"{kuasarr_base_url}{REGISTER_ENDPOINT}{handler_id}",
            timeout=5,
        )


def test_parallel_poll_unknown_handler_returns_409(kuasarr_base_url: str, kuasarr_status: Dict):
    response = requests.get(
        f"{kuasarr_base_url}{PARALLEL_POLL_ENDPOINT}",
        headers={"X-Capha-Handler": "pytest-unknown"},
        timeout=5,
    )
    assert response.status_code == 409
    body = response.json()
    assert body.get("error") == "Unbekannter Handler"
    assert "poll_after" in body


def test_register_handler_visible_in_status(kuasarr_base_url: str, kuasarr_status: Dict, registered_handler: str):
    status_response = requests.get(f"{kuasarr_base_url}{STATUS_ENDPOINT}", timeout=5)
    assert status_response.status_code == 200
    status_payload = status_response.json()
    handler_ids = {entry.get("handler_id") for entry in status_payload.get("handler_metrics", [])}
    assert registered_handler in handler_ids


def test_registered_handler_poll_without_jobs(kuasarr_base_url: str, registered_handler: str):
    response = requests.get(
        f"{kuasarr_base_url}{PARALLEL_POLL_ENDPOINT}",
        headers={"X-Capha-Handler": registered_handler},
        timeout=5,
    )
    # Ohne vorhandene Jobs liefert Kuasarr 404 inklusive Poll-Timer
    assert response.status_code in {200, 404}
    payload = response.json()
    assert "poll_after" in payload
    if response.status_code == 200:
        assert "jobs" in payload and isinstance(payload["jobs"], list)
    else:
        assert payload.get("jobs") == []
