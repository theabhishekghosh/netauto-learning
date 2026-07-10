import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from week5_day23 import app
from starlette.testclient import TestClient

client = TestClient(app)
API_KEY = "netauto-secret-2026"
HEADERS = {"X-API-Key": API_KEY}


# ── Health check (public endpoint) ──────────────────────────────

def test_root_returns_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ── Authentication ───────────────────────────────────────────────

def test_inventory_requires_auth():
    """No API key — should be rejected."""
    response = client.get("/inventory")
    assert response.status_code == 401


def test_inventory_rejects_wrong_key():
    """Wrong API key — should be rejected."""
    response = client.get("/inventory", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401


# ── Device facts endpoint ────────────────────────────────────────

def test_device_facts_returns_correct_data():
    """GET /device/{host}/facts — should return device summary."""
    mock_summary = {
        "hostname": "PE1_RE",
        "role": "PE",
        "model": "MX240",
        "version": "24.4R2-S3.2",
        "uptime": "1 day, 2 hours"
    }

    with patch("week5_day23.NetworkDevice") as MockNetworkDevice:
        mock_device = MagicMock()
        mock_device.get_summary.return_value = mock_summary
        mock_device.__enter__ = MagicMock(return_value=mock_device)
        mock_device.__exit__ = MagicMock(return_value=False)
        MockNetworkDevice.return_value = mock_device

        response = client.get(
            "/device/10.207.194.11/facts",
            headers=HEADERS
        )

    assert response.status_code == 200
    data = response.json()
    assert data["hostname"] == "PE1_RE"
    assert data["model"] == "MX240"


def test_device_facts_returns_503_on_connection_failure():
    """GET /device/{host}/facts — unreachable device should return 503."""
    from jnpr.junos.exception import ConnectError

    mock_host = MagicMock()
    mock_host.hostname = "10.207.194.11"

    with patch("week5_day23.NetworkDevice") as MockNetworkDevice:
        mock_device = MagicMock()
        mock_device.__enter__ = MagicMock(
            side_effect=ConnectError(mock_host)
        )
        mock_device.__exit__ = MagicMock(return_value=False)
        MockNetworkDevice.return_value = mock_device

        response = client.get(
            "/device/10.207.194.11/facts",
            headers=HEADERS
        )

    assert response.status_code == 503


# ── Deploy endpoint ──────────────────────────────────────────────

def test_deploy_returns_success_with_diff():
    """POST /deploy — valid config should return diff."""
    with patch("week5_day23.NetworkDevice") as MockNetworkDevice:
        mock_device = MagicMock()
        mock_device.deploy_dry_run.return_value = "[edit interfaces]\n+  ge-0/0/9"
        mock_device.__enter__ = MagicMock(return_value=mock_device)
        mock_device.__exit__ = MagicMock(return_value=False)
        MockNetworkDevice.return_value = mock_device

        response = client.post(
            "/deploy",
            json={
                "host": "10.207.194.11",
                "config": "set interfaces ge-0/0/9 unit 0 description test"
            },
            headers=HEADERS
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "diff" in data


def test_deploy_returns_no_changes_when_diff_is_none():
    """POST /deploy — no diff means no changes needed."""
    with patch("week5_day23.NetworkDevice") as MockNetworkDevice:
        mock_device = MagicMock()
        mock_device.deploy_dry_run.return_value = None  # ← no diff
        mock_device.__enter__ = MagicMock(return_value=mock_device)
        mock_device.__exit__ = MagicMock(return_value=False)
        MockNetworkDevice.return_value = mock_device

        response = client.post(
            "/deploy",
            json={
                "host": "10.207.194.11",
                "config": "set interfaces ge-0/0/9 unit 0 description test"
            },
            headers=HEADERS
        )

    assert response.status_code == 200
    assert response.json()["status"] == "no_changes"