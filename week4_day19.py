import time
from concurrent.futures import ThreadPoolExecutor
from jnpr.junos.exception import ConnectError
from week1_day6 import NetworkDevice
import logging
logging.getLogger("paramiko").setLevel(logging.CRITICAL)


def poll_one_device(device: NetworkDevice) -> dict:
    """
    Connect to one device, fetch summary, disconnect.

    Args:
        device: NetworkDevice object (not yet connected)

    Returns:
        Device summary dict, or error dict if connection failed
    """
    try:
        device.connect()
        summary = device.get_summary()
        device.disconnect()
        return summary
    except ConnectError as e:
        return {"hostname": device.host, "error": str(e)}
    except Exception as e:
        return {"hostname": device.host, "role": device.role, "error": f"Unexpected: {str(e)}"}


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
        NetworkDevice("10.49.0.254",  "CE", "labroot", "lab123"),
        NetworkDevice("10.49.0.197",  "CE", "labroot", "lab123"),
    ]

    start = time.time()

    with ThreadPoolExecutor(max_workers=12) as executor:
        results = list(executor.map(poll_one_device, devices))

    end = time.time()

    for result in results:
        print(result)

    print(f"\nConcurrent inventory collection completed in {end - start:.2f} seconds.")