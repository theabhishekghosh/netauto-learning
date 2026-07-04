from jnpr.junos import Device
from jnpr.junos.exception import ConnectError

def connect_device(host: str, user: str, password: str) -> Device: 
    """
    Connect to a Junos device using PyEZ.

    Args:
        host: Device management IP
        user: Login username
        password: Login password

    Returns:
        Connected Device object which is not actually needed when context manager is used, but included for demonstration purposes.
    """
    dev = Device(host=host, user=user, password=password)
    dev.open()
    return dev

def get_device_facts(dev: Device) -> dict:
    """
    Retrieve basic device facts.

    Args:
        dev: Connected PyEZ Device object

    Returns:
        Dictionary of device facts
    """
    return {
        "hostname": dev.facts["hostname"],
        "model": dev.facts["model"],
        "version": dev.facts["version"],
        "uptime": dev.facts["RE0"]["up_time"],
    }

if __name__ == "__main__":
    HOST = "10.207.194.11"
    USER = "labroot"
    PASSWORD = "lab123"

    try:
        with Device(host=HOST, user=USER, password=PASSWORD) as dev:
            facts = get_device_facts(dev)
            print(f"Hostname : {facts['hostname']}")
            print(f"Model    : {facts['model']}")
            print(f"Version  : {facts['version']}")
            print(f"Uptime   : {facts['uptime']}")
    except ConnectError as e:
        print(f"Connection failed: {e}")