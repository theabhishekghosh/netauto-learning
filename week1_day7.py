from jnpr.junos.exception import ConnectError
from week1_day6 import  NetworkDevice
import time

def collect_inventory(devices: list) -> list[dict]:
    """
    Collect facts from all devices.

    Args:
        devices: List of NetworkDevice objects

    Returns:
        List of device summary dictionaries
    """
    inventory = []
    for device in devices:
        try:
            device.connect()
            inventory.append(device.get_summary())
            device.disconnect()
        except ConnectError as e:
            print(f"Failed to connect to {device.host}: {e}")
    return inventory

def print_inventory(inventory: list[dict]) -> None:
    """
    Print inventory in a formatted table.

    Args:
        inventory: List of device summary dictionaries
    """
    print(f"\n{'Hostname':<12} {'Role':<6} {'Model':<8} {'Version':<14} {'Uptime'}")
    print("-" * 70)
    for summary in inventory:
        print(f"{summary['hostname']:<12} {summary['role']:<6} {summary['model']:<8} {summary['version']:<14} {summary['uptime']}")

if __name__ == "__main__":
    devices = [
    NetworkDevice("10.207.194.11",  "PE", "labroot", "lab123"),
    NetworkDevice("10.207.194.94", "PE", "labroot", "lab123"),
    NetworkDevice("10.207.195.43", "PE", "labroot", "lab123"),
    NetworkDevice("10.207.194.92",  "P",  "labroot", "lab123"),
    NetworkDevice("10.207.205.22",  "PE", "labroot", "lab123"),
    NetworkDevice("10.207.207.208", "PE", "labroot", "lab123"),
    NetworkDevice("10.207.210.187", "PE", "labroot", "lab123"),
    NetworkDevice("10.207.213.128",  "CE", "labroot", "lab123"),
    NetworkDevice("10.207.208.59", "CE", "labroot", "lab123"),
    NetworkDevice("10.207.206.34",   "CE", "labroot", "lab123"),
    NetworkDevice("10.207.216.116",  "CE", "labroot", "lab123"),
]
    start_time = time.time()
    results = collect_inventory(devices)
    print_inventory(results)
    end_time = time.time()
    print(f"\nInventory collection completed in {end_time - start_time:.2f} seconds.")