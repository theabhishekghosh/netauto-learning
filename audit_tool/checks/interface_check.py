# audit_tool/checks/interface_check.py
import logging
from audit_tool.checks.models import Finding, CheckResult, CheckStatus, Severity

logger = logging.getLogger(__name__)


def check_ce_interface_hygiene(
    device_configs: list[dict],
    device_inventory: list[dict]
) -> CheckResult:
    """
    Check CE-facing interfaces for misconfigurations:
    1. Must NOT be in OSPF area 0
    2. Must NOT have family mpls

    Args:
        device_configs: List of parsed config dicts
        device_inventory: List of device dicts from device_inventory.yaml

    Returns:
        CheckResult with findings for any misconfigured CE interfaces
    """
    findings = []
    devices_checked = 0

    # build lookup: hostname -> ce_interfaces list
    ce_map = {
        d["hostname"]: d.get("ce_interfaces", [])
        for d in device_inventory
    }

    for config in device_configs:
        hostname = config.get("hostname", "unknown")
        ce_interfaces = ce_map.get(hostname, [])

        if not ce_interfaces:
            continue  # no CE interfaces on this device

        devices_checked += 1

        # collect all OSPF interfaces across all areas
        ospf_interfaces = []
        for area, data in config.get("ospf", {}).get("areas", {}).items():
            ospf_interfaces.extend(data.get("interfaces", []))

        mpls_interfaces = config.get("mpls", {}).get("interfaces", [])

        for ce_intf in ce_interfaces:
            ce_intf_unit = f"{ce_intf}.0"

            # check OSPF — CE interface should not be in OSPF area 0
            if ce_intf_unit in ospf_interfaces or ce_intf in ospf_interfaces:
                findings.append(Finding(
                    device=hostname,
                    check="ce_interface_hygiene",
                    severity=Severity.MEDIUM,
                    message=f"CE-facing interface {ce_intf} is in OSPF area 0",
                    detail=(
                        f"{ce_intf} is defined as a CE-facing interface "
                        f"but appears in OSPF area 0.0.0.0. "
                        f"CE interfaces should not participate in the backbone IGP."
                    )
                ))
                logger.warning(f"{hostname} CE interface {ce_intf} in OSPF area 0")

            # check MPLS — CE interface should not have family mpls
            if ce_intf_unit in mpls_interfaces or ce_intf in mpls_interfaces:
                findings.append(Finding(
                    device=hostname,
                    check="ce_interface_hygiene",
                    severity=Severity.MEDIUM,
                    message=f"CE-facing interface {ce_intf} has family mpls",
                    detail=(
                        f"{ce_intf} is defined as a CE-facing interface "
                        f"but has MPLS enabled. "
                        f"CE interfaces should not carry MPLS labels."
                    )
                ))
                logger.warning(f"{hostname} CE interface {ce_intf} has MPLS")

    status = CheckStatus.FAIL if findings else CheckStatus.PASS
    return CheckResult(
        check_name="ce_interface_hygiene",
        status=status,
        findings=findings,
        devices_checked=devices_checked
    )