
def format_interface_status(interface: str, status: str) -> str:
    """
    This function takes an interface name and its status, and returns a formatted string.
    
    Args:
        interface (str): The name of the interface (e.g., "Ethernet0/0").
        status (str): The status of the interface (e.g., "up", "down").
      
    Returns:
        str: A formatted string combining the interface name and its status.
    """
    return f"Interface {interface} is {status}."

def is_interface_up(status: str) -> bool:
    """
    This function returns true if the interface status is "up", and false otherwise.

    Args:
        status (str): The status of the interface (e.g., "up", "down").
    
    Returns:
        True if the status is "up", False otherwise.
    """
    if not status.strip():
        raise ValueError("Status cannot be empty")
    return status.strip().lower() == "up"


if __name__ == "__main__":
    print(format_interface_status("ge-0/0/0", "up"))
    print(format_interface_status("ge-0/0/1", "down"))
    print(is_interface_up("up"))
    print(is_interface_up("down"))
    print(is_interface_up("UP"))    
    print(is_interface_up("  up ")) 
    try:
     print(is_interface_up(""))
    except ValueError as e:
     print(f"Error: {e}")