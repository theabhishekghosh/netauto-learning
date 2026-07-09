from unittest.mock import patch, MagicMock
from jnpr.junos.exception import ConnectError
from week1_day6 import NetworkDevice


def test_get_summary_returns_correct_structure():
    with patch("week1_day6.Device") as MockDevice:
        mock_dev = MagicMock()
        mock_dev.facts = {
            "hostname": "PE1_RE",
            "model": "MX240",
            "version": "24.4R2-S3.2",
            "RE0": {"up_time": "1 day, 2 hours"}
        }
        MockDevice.return_value = mock_dev
        device = NetworkDevice("10.207.194.11", "PE", "labroot", "lab123")
        device.connect()
        result = device.get_summary()

    assert result["hostname"] == "PE1_RE"
    assert result["model"] == "MX240"
    assert result["role"] == "PE"
    assert result["version"] == "24.4R2-S3.2"


def test_connect_raises_on_failure():
    """connect() should re-raise ConnectError when device is unreachable."""
    with patch("week1_day6.Device") as MockDevice:
        mock_dev = MagicMock()
        mock_dev.open.side_effect = ConnectError("10.207.194.11")
        MockDevice.return_value = mock_dev

        device = NetworkDevice("10.207.194.11", "PE", "labroot", "lab123")

        import pytest
        with pytest.raises(ConnectError):
            device.connect()


def test_get_bgp_neighbors_returns_established_peers():
    """get_bgp_neighbors() should parse XML and return peer list."""
    from lxml import etree

    fake_xml = etree.fromstring("""
        <bgp-information>
            <bgp-peer>
                <peer-address>4.4.4.4</peer-address>
                <peer-state>Established</peer-state>
            </bgp-peer>
        </bgp-information>
    """)

    with patch("week1_day6.Device") as MockDevice:
        mock_dev = MagicMock()
        mock_dev.facts = {
            "hostname": "PE1_RE", "model": "MX240",
            "version": "24.4R2-S3.2", "RE0": {"up_time": "1 day"}
        }
        mock_dev.rpc.get_bgp_summary_information.return_value = fake_xml
        MockDevice.return_value = mock_dev

        device = NetworkDevice("10.207.194.11", "PE", "labroot", "lab123")
        device.connect()
        result = device.get_bgp_neighbors()

    assert len(result) == 1
    assert result[0]["peer"] == "4.4.4.4"
    assert result[0]["state"] == "Established"