import pytest
from week2_day8 import find_problem_interfaces


def test_find_problem_interfaces_returns_admin_up_oper_down():
    """Classic fault — admin up but operationally down."""
    interfaces = [
        {"name": "ge-0/0/0", "oper": "up",   "admin": "up"},
        {"name": "ge-0/0/1", "oper": "down", "admin": "up"},
        {"name": "ge-0/0/2", "oper": "up",   "admin": "up"},
    ]
    result = find_problem_interfaces(interfaces)
    assert len(result) == 1
    assert result[0]["name"] == "ge-0/0/1"


def test_find_problem_interfaces_ignores_admin_down():
    """Admin-down interfaces are intentional — not a problem."""
    interfaces = [
        {"name": "ge-0/0/0", "oper": "down", "admin": "down"},
    ]
    result = find_problem_interfaces(interfaces)
    assert result == []


def test_find_problem_interfaces_empty_input():
    assert find_problem_interfaces([]) == []


def test_find_problem_interfaces_all_healthy():
    interfaces = [
        {"name": "ge-0/0/0", "oper": "up", "admin": "up"},
        {"name": "ge-0/0/1", "oper": "up", "admin": "up"},
    ]
    assert find_problem_interfaces(interfaces) == []


def test_find_problem_interfaces_multiple_problems():
    interfaces = [
        {"name": "ge-0/0/0", "oper": "down", "admin": "up"},
        {"name": "ge-0/0/1", "oper": "down", "admin": "up"},
        {"name": "ge-0/0/2", "oper": "up",   "admin": "up"},
    ]
    result = find_problem_interfaces(interfaces)
    assert len(result) == 2
    names = [r["name"] for r in result]
    assert "ge-0/0/0" in names
    assert "ge-0/0/1" in names