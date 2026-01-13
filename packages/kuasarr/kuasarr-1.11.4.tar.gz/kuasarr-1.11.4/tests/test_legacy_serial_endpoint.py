import os

import pytest
import requests

LEGACY_ENDPOINT = "/captchasolverr/api/to_decrypt/"
STATUS_ENDPOINT = "/captchasolverr/api/status/"
HELPER_STATUS_ENDPOINT = "/captchasolverr/api/set_sponsor_status/"


def _base_url() -> str:
    return os.environ.get("KUASARR_URL", "http://127.0.0.1:8080").rstrip("/")


@pytest.fixture(scope="module")
def kuasarr_available() -> str:
    base_url = _base_url()
    try:
        status_resp = requests.get(f"{base_url}{STATUS_ENDPOINT}", timeout=5)
    except requests.ConnectionError as exc:
        pytest.skip(f"Kuasarr nicht erreichbar: {exc}")

    if status_resp.status_code not in {200, 404}:
        pytest.skip(
            f"Status-Endpoint liefert unerwarteten Code: {status_resp.status_code}"
        )
    return base_url


def test_legacy_to_decrypt_smoke(kuasarr_available: str):
    response = requests.get(f"{kuasarr_available}{LEGACY_ENDPOINT}", timeout=5)

    assert response.status_code in {200, 403, 404}

    if response.status_code == 200:
        payload = response.json()
        assert "to_decrypt" in payload
        assert payload["to_decrypt"].get("name")
        assert payload["to_decrypt"].get("url")
    elif response.status_code == 403:
        assert "CaptchaHelper" in response.text


def _set_helper_state(base_url: str, active: bool) -> None:
    response = requests.put(
        f"{base_url}{HELPER_STATUS_ENDPOINT}",
        json={"activate": bool(active)},
        timeout=5,
    )
    assert response.status_code == 200, response.text


@pytest.fixture
def helper_controlled_base(kuasarr_available: str):
    try:
        _set_helper_state(kuasarr_available, False)
    except AssertionError as exc:
        pytest.skip(f"Setzen des Helper-Status fehlgeschlagen: {exc}")

    yield kuasarr_available

    # Nach den Tests wieder deaktivieren, um globalen Zustand zu vermeiden
    try:
        _set_helper_state(kuasarr_available, False)
    except AssertionError:
        pass


def test_legacy_requires_helper_active(helper_controlled_base: str):
    _set_helper_state(helper_controlled_base, False)
    response = requests.get(f"{helper_controlled_base}{LEGACY_ENDPOINT}", timeout=5)

    assert response.status_code == 403
    assert "CaptchaHelper" in response.text


def test_legacy_returns_404_when_active_without_packages(helper_controlled_base: str):
    _set_helper_state(helper_controlled_base, True)
    response = requests.get(f"{helper_controlled_base}{LEGACY_ENDPOINT}", timeout=5)

    assert response.status_code in {200, 404}
    if response.status_code == 200:
        payload = response.json()
        assert payload.get("to_decrypt")
        assert payload["to_decrypt"].get("name")
    else:
        assert response.text
