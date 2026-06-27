from jnpr.junos.exception import ConnectError
from week1_day6 import  NetworkDevice

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
    NetworkDevice("10.49.0.137",  "PE", "labroot", "lab123"),
    NetworkDevice("10.49.16.181", "PE", "labroot", "lab123"),
    NetworkDevice("10.49.16.140", "PE", "labroot", "lab123"),
    NetworkDevice("10.49.16.84",  "P",  "labroot", "lab123"),
    NetworkDevice("10.49.25.94",  "PE", "labroot", "lab123"),
    NetworkDevice("10.49.15.198", "PE", "labroot", "lab123"),
    NetworkDevice("10.49.15.126", "PE", "labroot", "lab123"),
    NetworkDevice("10.49.16.48",  "CE", "labroot", "lab123"),
    NetworkDevice("10.49.15.128", "CE", "labroot", "lab123"),
    NetworkDevice("10.49.0.99",   "CE", "labroot", "lab123"),
    NetworkDevice("10.49.0.197",  "CE", "labroot", "lab123"),
]
    results = collect_inventory(devices)
    print_inventory(results)