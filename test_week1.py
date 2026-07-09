import pytest
from week1 import format_interface_status, is_interface_up
from week1_day3 import get_down_interfaces
from week1_day4 import is_down, format_alert


# ── format_interface_status ──────────────────────────────────────

def test_format_interface_status_returns_string():
    result = format_interface_status("ge-0/0/0", "up")
    assert isinstance(result, str)


def test_format_interface_status_contains_interface_name():
    result = format_interface_status("ge-0/0/0", "up")
    assert "ge-0/0/0" in result


def test_format_interface_status_contains_status():
    result = format_interface_status("ge-0/0/0", "down")
    assert "down" in result


# ── is_interface_up ──────────────────────────────────────────────

def test_is_interface_up_returns_true_for_up():
    assert is_interface_up("up") is True


def test_is_interface_up_returns_false_for_down():
    assert is_interface_up("down") is False


def test_is_interface_up_case_insensitive():
    assert is_interface_up("UP") is True
    assert is_interface_up("Up") is True


def test_is_interface_up_strips_whitespace():
    assert is_interface_up("  up  ") is True


def test_is_interface_up_raises_on_empty():
    with pytest.raises(ValueError):
        is_interface_up("")


# ── get_down_interfaces ──────────────────────────────────────────

def test_get_down_interfaces_returns_only_down():
    interfaces = [
        {"name": "ge-0/0/0", "status": "up"},
        {"name": "ge-0/0/1", "status": "down"},
        {"name": "ge-0/0/2", "status": "up"},
    ]
    result = get_down_interfaces(interfaces)
    assert result == ["ge-0/0/1"]


def test_get_down_interfaces_empty_list():
    assert get_down_interfaces([]) == []


def test_get_down_interfaces_all_up():
    interfaces = [
        {"name": "ge-0/0/0", "status": "up"},
        {"name": "ge-0/0/1", "status": "up"},
    ]
    assert get_down_interfaces(interfaces) == []


def test_get_down_interfaces_missing_status_key():
    interfaces = [{"name": "ge-0/0/0"}]  # no status key
    result = get_down_interfaces(interfaces)
    assert result == []


# ── is_down ──────────────────────────────────────────────────────

def test_is_down_returns_true_for_down():
    assert is_down({"name": "ge-0/0/0", "status": "down"}) is True


def test_is_down_returns_false_for_up():
    assert is_down({"name": "ge-0/0/0", "status": "up"}) is False


# ── format_alert ─────────────────────────────────────────────────

def test_format_alert_contains_interface_name():
    result = format_alert("ge-0/0/1")
    assert "ge-0/0/1" in result