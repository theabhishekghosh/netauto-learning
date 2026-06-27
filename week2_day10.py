from week1_day6 import NetworkDevice
from jnpr.junos.exception import ConnectError


def find_problem_interfaces(interfaces: list[dict]) -> list[dict]:
    """Find interfaces admin-up but oper-down."""
    return [
        intf for intf in interfaces
        if intf["admin"] == "up" and intf["oper"] == "down"
    ]


def find_down_bgp_peers(peers: list[dict]) -> list[dict]:
    """Find BGP peers not Established."""
    return [peer for peer in peers if peer["state"] != "Established"]


def check_device(device: NetworkDevice) -> dict:
    """
    Run a full health check on one device.

    Args:
        device: NetworkDevice object (not yet connected)

    Returns:
        Dict with summary, problem interfaces, and down BGP peers
    """
    device.connect()
    summary = device.get_summary()
    interfaces = device.get_interfaces()
    bgp_peers = device.get_bgp_neighbors()
    device.disconnect()

    return {
        "summary": summary,
        "problem_interfaces": find_problem_interfaces(interfaces),
        "down_bgp_peers": find_down_bgp_peers(bgp_peers),
    }


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

    for device in devices:
        try:
            report = check_device(device)
            hostname = report["summary"]["hostname"]
            print(f"\n=== {hostname} ({report['summary']['role']}) ===")

            if report["problem_interfaces"]:
                print("  Problem interfaces:")
                for intf in report["problem_interfaces"]:
                    print(f"    {intf['name']}")

            if report["down_bgp_peers"]:
                print("  Down BGP peers:")
                for peer in report["down_bgp_peers"]:
                    print(f"    {peer['peer']} - {peer['state']}")

            if not report["problem_interfaces"] and not report["down_bgp_peers"]:
                print("  No issues found")

        except ConnectError as e:
            print(f"\n=== {device.host} ===")
            print(f"  Connection failed: {e}")