from week1_day6 import NetworkDevice

def find_problem_interfaces(interfaces: list[dict]) -> list[dict]:
    """
    Find interfaces that are admin up but operationally down — a real fault signal.

    Args:
        interfaces: List of interface dicts with name, oper, admin

    Returns:
        List of problem interfaces
    """
    return [
        intf for intf in interfaces
        if intf["admin"] == "up" and intf["oper"] == "down"
    ]

if __name__ == "__main__":
    pe1 = NetworkDevice("10.207.194.11", "PE", "labroot", "lab123")
    pe1.connect()
    interfaces = pe1.get_interfaces()
    for intf in interfaces:
         print(intf)
    pe1.disconnect()
    problems = find_problem_interfaces(interfaces)
    print(f"\n{len(problems)} interfaces are admin-up but oper-down:")
    for p in problems:
        print(f"  {p['name']}")