
def get_down_interfaces(interfaces: list[dict]) -> list[str]:  
    """Returns a list of interfaces that are down.
    
    Args:
        interfaces: A list of dictionaries, where each dictionary contains the interface name and its status.
    
    Returns:
        A list of interface names that are down.
    """
    return [interface.get("name", "") for interface in interfaces if interface.get("status", "").lower() == "down"]

if __name__ == "__main__":
    interfaces = [
    {"name": "ge-0/0/0", "status": "up"},
    {"name": "ge-0/0/1", "status": "down"},
    {"name": "ge-0/0/2", "status": "up"},
]
    down_interfaces = get_down_interfaces(interfaces)
    print("Down interfaces:", down_interfaces)
    print(get_down_interfaces([]))  # empty list
    broken = [
    {"name": "ge-0/0/0"},  # missing status key
]
print(get_down_interfaces(broken))