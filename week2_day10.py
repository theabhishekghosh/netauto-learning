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