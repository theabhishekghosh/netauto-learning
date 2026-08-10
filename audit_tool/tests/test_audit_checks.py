# audit_tool/tests/test_audit_checks.py
import pytest
from audit_tool.checks.models import Severity, CheckStatus
from audit_tool.checks.bgp_check import check_bgp_export_consistency
from audit_tool.checks.interface_check import check_ce_interface_hygiene


# ── helpers — reusable test data ─────────────────────────────────

def make_pe_config(hostname: str, export_policies: list) -> dict:
    """Build a minimal PE config dict for testing."""
    return {
        "hostname": hostname,
        "bgp": {
            "groups": {
                "internal": {
                    "export_policies": export_policies,
                    "neighbors": ["4.4.4.4"]
                }
            }
        },
        "ospf": {"areas": {"0.0.0.0": {"interfaces": ["ge-0/0/0.0", "lo0.0"]}}},
        "mpls": {"interfaces": ["ge-0/0/0.0"]},
        "interfaces": {},
        "rsvp": {"enabled": True},
        "routing_options": {"router_id": "1.1.1.1", "autonomous_system": "65001"}
    }


def make_rr_config(hostname: str, export_policies: list) -> dict:
    """Build a minimal RR config dict for testing."""
    return {
        "hostname": hostname,
        "bgp": {
            "groups": {
                "rrc": {
                    "export_policies": export_policies,
                    "neighbors": ["1.1.1.1", "2.2.2.2"]
                }
            }
        },
        "ospf": {"areas": {"0.0.0.0": {"interfaces": ["ge-0/0/0.0", "ge-0/0/1.0"]}}},
        "mpls": {"interfaces": ["ge-0/0/0.0", "ge-0/0/1.0"]},
        "interfaces": {},
        "rsvp": {"enabled": True},
        "routing_options": {"router_id": "4.4.4.4", "autonomous_system": "65001"}
    }


# ── BGP export consistency tests ─────────────────────────────────

def test_bgp_check_passes_when_all_correct():
    """All PEs have NHS, RR has no NHS — should pass."""
    configs = [
        make_pe_config("PE1_RE", ["NHS"]),
        make_pe_config("PE2_RE", ["NHS"]),
        make_rr_config("P4_RE",  []),       # RR correctly has no NHS
    ]
    result = check_bgp_export_consistency(configs)
    assert result.status == CheckStatus.PASS
    assert len(result.findings) == 0
    assert result.devices_checked == 3


def test_bgp_check_flags_missing_nhs_on_pe():
    """PE missing NHS — should produce MEDIUM finding."""
    configs = [
        make_pe_config("PE1_RE", ["NHS"]),
        make_pe_config("PE5_RE", []),        # ← missing NHS
        make_rr_config("P4_RE",  []),
    ]
    result = check_bgp_export_consistency(configs)
    assert result.status == CheckStatus.FAIL
    assert len(result.findings) == 1
    assert result.findings[0].device == "PE5_RE"
    assert result.findings[0].severity == Severity.MEDIUM


def test_bgp_check_flags_nhs_on_rr():
    """RR has NHS — should produce HIGH finding."""
    configs = [
        make_pe_config("PE1_RE", ["NHS"]),
        make_rr_config("P4_RE",  ["NHS"]),   # ← RR incorrectly has NHS
    ]
    result = check_bgp_export_consistency(configs)
    assert result.status == CheckStatus.FAIL
    assert len(result.findings) == 1
    assert result.findings[0].device == "P4_RE"
    assert result.findings[0].severity == Severity.HIGH


def test_bgp_check_flags_both_issues():
    """Both PE missing NHS and RR has NHS — should produce 2 findings."""
    configs = [
        make_pe_config("PE1_RE", ["NHS"]),
        make_pe_config("PE5_RE", []),        # ← missing NHS
        make_rr_config("P4_RE",  ["NHS"]),   # ← RR has NHS
    ]
    result = check_bgp_export_consistency(configs)
    assert result.status == CheckStatus.FAIL
    assert len(result.findings) == 2
    devices = [f.device for f in result.findings]
    assert "PE5_RE" in devices
    assert "P4_RE" in devices


def test_bgp_check_pe_with_multiple_export_policies():
    """PE with NHS plus another policy — should still pass."""
    configs = [
        make_pe_config("PE7_RE", ["NHS", "bgp_to_ospf"]),  # NHS present
        make_rr_config("P4_RE",  []),
    ]
    result = check_bgp_export_consistency(configs)
    assert result.status == CheckStatus.PASS
    assert len(result.findings) == 0


def test_bgp_check_empty_device_list():
    """No devices — should skip."""
    result = check_bgp_export_consistency([])
    assert result.status == CheckStatus.PASS
    assert result.devices_checked == 0


# ── CE interface hygiene tests ───────────────────────────────────

def make_inventory(hostname: str, ce_interfaces: list) -> dict:
    """Build a minimal device inventory entry for testing."""
    return {
        "hostname": hostname,
        "role": "PE",
        "ce_interfaces": ce_interfaces
    }


def test_ce_check_passes_when_no_ce_in_ospf():
    """CE interface not in OSPF — should pass."""
    configs = [
        {
            "hostname": "PE3_RE",
            "ospf": {"areas": {"0.0.0.0": {"interfaces": ["ge-0/0/0.0", "ge-0/0/1.0"]}}},
            "mpls": {"interfaces": ["ge-0/0/0.0", "ge-0/0/1.0"]},
            "bgp": {"groups": {}}, "interfaces": {}, "rsvp": {"enabled": True},
            "routing_options": {"router_id": "3.3.3.3", "autonomous_system": "65001"}
        }
    ]
    inventory = [make_inventory("PE3_RE", ["ge-0/0/2"])]
    result = check_ce_interface_hygiene(configs, inventory)
    assert result.status == CheckStatus.PASS
    assert len(result.findings) == 0


def test_ce_check_flags_ce_interface_in_ospf():
    """CE interface in OSPF area 0 — should produce MEDIUM finding."""
    configs = [
        {
            "hostname": "PE3_RE",
            "ospf": {"areas": {"0.0.0.0": {
                "interfaces": ["ge-0/0/0.0", "ge-0/0/1.0", "ge-0/0/2.0"]  # ← CE in OSPF
            }}},
            "mpls": {"interfaces": ["ge-0/0/0.0", "ge-0/0/1.0"]},
            "bgp": {"groups": {}}, "interfaces": {}, "rsvp": {"enabled": True},
            "routing_options": {"router_id": "3.3.3.3", "autonomous_system": "65001"}
        }
    ]
    inventory = [make_inventory("PE3_RE", ["ge-0/0/2"])]
    result = check_ce_interface_hygiene(configs, inventory)
    assert result.status == CheckStatus.FAIL
    assert len(result.findings) == 1
    assert result.findings[0].device == "PE3_RE"
    assert result.findings[0].severity == Severity.MEDIUM
    assert "ge-0/0/2" in result.findings[0].message


def test_ce_check_flags_ce_interface_with_mpls():
    """CE interface with family mpls — should produce MEDIUM finding."""
    configs = [
        {
            "hostname": "PE3_RE",
            "ospf": {"areas": {"0.0.0.0": {"interfaces": ["ge-0/0/0.0"]}}},
            "mpls": {"interfaces": ["ge-0/0/0.0", "ge-0/0/2.0"]},  # ← CE has MPLS
            "bgp": {"groups": {}}, "interfaces": {}, "rsvp": {"enabled": True},
            "routing_options": {"router_id": "3.3.3.3", "autonomous_system": "65001"}
        }
    ]
    inventory = [make_inventory("PE3_RE", ["ge-0/0/2"])]
    result = check_ce_interface_hygiene(configs, inventory)
    assert result.status == CheckStatus.FAIL
    assert len(result.findings) == 1
    assert result.findings[0].severity == Severity.MEDIUM


def test_ce_check_skips_devices_with_no_ce_interfaces():
    """Device with no CE interfaces — should not be checked."""
    configs = [make_pe_config("PE1_RE", ["NHS"])]
    inventory = [make_inventory("PE1_RE", [])]  # ← no CE interfaces
    result = check_ce_interface_hygiene(configs, inventory)
    assert result.status == CheckStatus.PASS
    assert result.devices_checked == 0


# ── Config parser tests ───────────────────────────────────────────

def test_parser_extracts_bgp_export_policy():
    """Parser correctly extracts BGP export policy."""
    from audit_tool.parsers.config_parser import parse_set_format
    config_text = """
set protocols bgp group internal export NHS
set protocols bgp group internal neighbor 4.4.4.4 peer-as 65001
"""
    result = parse_set_format(config_text)
    assert "internal" in result["bgp"]["groups"]
    assert "NHS" in result["bgp"]["groups"]["internal"]["export_policies"]
    assert "4.4.4.4" in result["bgp"]["groups"]["internal"]["neighbors"]


def test_parser_detects_missing_export_policy():
    """Parser correctly shows empty export when no export configured."""
    from audit_tool.parsers.config_parser import parse_set_format
    config_text = """
set protocols bgp group internal neighbor 4.4.4.4 peer-as 65001
"""
    result = parse_set_format(config_text)
    assert "internal" in result["bgp"]["groups"]
    assert result["bgp"]["groups"]["internal"]["export_policies"] == []


def test_parser_extracts_ospf_interfaces():
    """Parser correctly extracts OSPF interfaces."""
    from audit_tool.parsers.config_parser import parse_set_format
    config_text = """
set protocols ospf area 0.0.0.0 interface ge-0/0/0.0
set protocols ospf area 0.0.0.0 interface ge-0/0/1.0
set protocols ospf area 0.0.0.0 interface lo0.0
"""
    result = parse_set_format(config_text)
    assert "0.0.0.0" in result["ospf"]["areas"]
    interfaces = result["ospf"]["areas"]["0.0.0.0"]["interfaces"]
    assert "ge-0/0/0.0" in interfaces
    assert "ge-0/0/1.0" in interfaces
    assert "lo0.0" in interfaces


def test_parser_handles_empty_config():
    """Parser handles empty input gracefully."""
    from audit_tool.parsers.config_parser import parse_set_format
    result = parse_set_format("")
    assert result["hostname"] is None
    assert result["bgp"]["groups"] == {}
    assert result["ospf"]["areas"] == {}