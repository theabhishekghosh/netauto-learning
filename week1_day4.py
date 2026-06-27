def is_down(interface: dict) -> bool:
    # checks one interface
    return interface.get("status", "").lower() == "down"

def get_down_interfaces(interfaces: list[dict]) -> list[str]:
    # uses is_down to filter
    return [interface.get("name", "") for interface in interfaces if is_down(interface)]

def format_alert(name: str) -> str:
    # formats the alert message
    return f"ALERT: Interface {name} is down!"

def process_device(interfaces: list[dict]) -> None:
    # orchestrates everything
    down_interfaces = get_down_interfaces(interfaces)
    for name in down_interfaces:
        alert_message = format_alert(name)
        print(alert_message)

if __name__ == "__main__":
    interfaces = [
    {"name": "ge-0/0/0", "status": "up"},
    {"name": "ge-0/0/1", "status": "down"},
    {"name": "ge-0/0/2", "status": "up"},
    {"name": "ge-0/0/3", "status": "down"},
]
    process_device(interfaces)