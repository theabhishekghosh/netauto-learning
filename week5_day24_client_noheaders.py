import requests

BASE_URL = "http://localhost:8000"

def get_inventory():
    """Call the inventory endpoint."""
    response = requests.get(f"{BASE_URL}/inventory")
    response.raise_for_status()
    return response.json()

def get_device_facts(host: str) -> dict:
    """Call the facts endpoint for a specific device."""
    response = requests.get(f"{BASE_URL}/device/{host}/facts")
    response.raise_for_status()
    return response.json()

def deploy_config(host: str, config: str, confirm_minutes: int = 1) -> dict:
    """Call the deploy endpoint."""
    response = requests.post(
        f"{BASE_URL}/deploy",
        json={
            "host": host,
            "config": config,
            "confirm_minutes": confirm_minutes
        }
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    # Test 1 — get facts for PE2
    print("=== PE2 Facts ===")
    facts = get_device_facts("10.207.194.94")
    print(facts)

    # Test 2 — get full inventory
    print("\n=== Inventory ===")
    inventory = get_inventory()
    for device in inventory:
        if "error" not in device:
            print(f"{device['hostname']:<12} {device['role']:<4} {device['version']}")

    # Test 3 — deploy a safe change
    print("\n=== Deploy ===")
    result = deploy_config(
        host="10.207.194.11",
        config="set interfaces ge-0/0/9 unit 0 description api-client-test"
    )
    print(result)