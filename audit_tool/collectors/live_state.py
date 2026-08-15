# audit_tool/collectors/live_state.py
import logging
from concurrent.futures import ThreadPoolExecutor
from jnpr.junos.exception import ConnectError
from week1_day6 import NetworkDevice

logger = logging.getLogger(__name__)


def collect_device_state(device_info: dict, user: str, password: str) -> dict:
    """
    Collect live config state from one device via PyEZ.
    Returns same structure as config_parser output.

    Args:
        device_info: Device dict from device_inventory.yaml
        user: SSH username
        password: SSH password

    Returns:
        Structured config dict matching config_parser output format
    """
    hostname = device_info["hostname"]
    host = device_info["management_ip"]

    try:
        with NetworkDevice(host, device_info["role"], user, password) as device:
            logger.info(f"Connected to {hostname} ({host})")

            # get BGP group config
            bgp_groups = device.get_bgp_group_config()

            # get OSPF interfaces
            ospf_areas = device.get_ospf_interfaces()

            # get MPLS interfaces
            mpls_interfaces = device.get_mpls_interfaces()

            # get facts
            facts = device.get_summary()

            return {
                "hostname": facts["hostname"],
                "bgp": {"groups": bgp_groups},
                "ospf": {"areas": ospf_areas},
                "mpls": {"interfaces": mpls_interfaces},
                "interfaces": {},
                "rsvp": {"enabled": True},
                "routing_options": {
                    "router_id": host,
                    "autonomous_system": "65001"
                }
            }

    except ConnectError as e:
        logger.error(f"Failed to connect to {hostname} ({host}): {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error for {hostname}: {e}")
        return {}


def collect_fleet_state(
    device_inventory: list[dict],
    user: str,
    password: str,
    max_workers: int = 7
) -> list[dict]:
    """
    Collect live state from all devices concurrently.

    Args:
        device_inventory: List of device dicts from device_inventory.yaml
        user: SSH username
        password: SSH password
        max_workers: Number of concurrent connections

    Returns:
        List of structured config dicts
    """
    logger.info(f"Starting concurrent live collection from {len(device_inventory)} devices")

    args = [(d, user, password) for d in device_inventory]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(
            lambda a: collect_device_state(*a), args
        ))

    # filter out empty results (failed connections)
    successful = [r for r in results if r]
    logger.info(f"Successfully collected from {len(successful)}/{len(device_inventory)} devices")

    return successful