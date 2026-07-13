# audit_tool/checks/bgp_check.py
import logging
from audit_tool.checks.models import Finding, CheckResult, CheckStatus, Severity

logger = logging.getLogger(__name__)


def check_bgp_export_consistency(device_configs: list[dict]) -> CheckResult:
    """
    Check BGP export policy consistency:
    1. All PE devices should have NHS on group 'internal'
    2. RR devices should NOT have NHS on group 'rrc'
    """
    findings = []
    devices_checked = 0

    for config in device_configs:
        hostname = config.get("hostname", "unknown")
        bgp_groups = config.get("bgp", {}).get("groups", {})
        devices_checked += 1

        # Check PE devices — group 'internal' should have NHS
        if "internal" in bgp_groups:
            export_policies = bgp_groups["internal"]["export_policies"]
            if "NHS" not in export_policies:
                findings.append(Finding(
                    device=hostname,
                    check="bgp_export_consistency",
                    severity=Severity.MEDIUM,
                    message="BGP export policy inconsistency on group 'internal'",
                    detail=(
                        f"Export policies: {export_policies} — "
                        f"most PEs have ['NHS']. Verify if intentional."
                    )
                ))
                logger.warning(f"{hostname} missing NHS on BGP group internal")

        # Check RR devices — group 'rrc' should NOT have NHS
        if "rrc" in bgp_groups:
            export_policies = bgp_groups["rrc"]["export_policies"]
            if "NHS" in export_policies:
                findings.append(Finding(
                    device=hostname,
                    check="bgp_export_consistency",
                    severity=Severity.HIGH,
                    message="Route Reflector has NHS on group 'rrc' — breaks next-hop transparency",
                    detail=(
                        f"RR should not modify next-hop. "
                        f"Current export policies: {export_policies}. "
                        f"Remove NHS from RR group."
                    )
                ))
                logger.warning(f"{hostname} RR has NHS — next-hop transparency broken")

    status = CheckStatus.FAIL if findings else CheckStatus.PASS
    return CheckResult(
        check_name="bgp_export_consistency",
        status=status,
        findings=findings,
        devices_checked=devices_checked
    )