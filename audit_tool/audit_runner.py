# audit_tool/audit_runner.py
import os
import yaml
import logging
import sys
from audit_tool.parsers.config_parser import load_device_config
from audit_tool.checks.bgp_check import check_bgp_export_consistency
from audit_tool.checks.interface_check import check_ce_interface_hygiene
from audit_tool.checks.models import AuditReport

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


def run_audit(inventory_path: str, snapshot_dir: str) -> AuditReport:
    """
    Run full config audit against offline config snapshots.

    Args:
        inventory_path: Path to device_inventory.yaml
        snapshot_dir: Directory containing device .cfg files

    Returns:
        AuditReport with all findings
    """
    # load inventory
    with open(inventory_path) as f:
        inventory = yaml.safe_load(f)

    network_name = inventory["network"]["name"]
    device_inventory = inventory["devices"]

    logger.info(f"Starting audit for: {network_name}")
    logger.info(f"Devices in inventory: {len(device_inventory)}")

    # load all device configs
    configs = []
    for device in device_inventory:
        config_file = os.path.join(
            os.path.dirname(inventory_path),
            device["config_file"]
        )
        config = load_device_config(config_file)
        if config:
            configs.append(config)
        else:
            logger.warning(f"Could not load config for {device['hostname']}")

    logger.info(f"Loaded {len(configs)} device configs successfully")

    # run checks
    report = AuditReport(network_name=network_name)

    logger.info("Running BGP export consistency check...")
    bgp_result = check_bgp_export_consistency(configs)
    report.check_results.append(bgp_result)
    logger.info(f"BGP check: {bgp_result.status.value} — {len(bgp_result.findings)} findings")

    logger.info("Running CE interface hygiene check...")
    intf_result = check_ce_interface_hygiene(configs, device_inventory)
    report.check_results.append(intf_result)
    logger.info(f"Interface check: {intf_result.status.value} — {len(intf_result.findings)} findings")

    # summary
    summary = report.summary()
    logger.info(f"Audit complete — {summary}")

    return report


if __name__ == "__main__":
    report = run_audit(
        inventory_path="audit_tool/inputs/device_inventory.yaml",
        snapshot_dir="audit_tool/inputs/snapshots"
    )

    print(f"\n{'='*60}")
    print(f"AUDIT REPORT — {report.network_name}")
    print(f"Generated: {report.generated_at}")
    print(f"{'='*60}")

    summary = report.summary()
    print(f"\nSUMMARY:")
    print(f"  Total findings : {summary['total_findings']}")
    print(f"  HIGH           : {summary['high']}")
    print(f"  MEDIUM         : {summary['medium']}")
    print(f"  LOW            : {summary['low']}")
    print(f"  INFO           : {summary['info']}")

    print(f"\nFINDINGS:")
    for result in report.check_results:
        print(f"\n  [{result.status.value}] {result.check_name} "
              f"({result.devices_checked} devices checked)")
        for f in result.findings:
            print(f"    [{f.severity.value}] {f.device}: {f.message}")
            print(f"    → {f.detail}")