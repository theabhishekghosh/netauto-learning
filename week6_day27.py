import sys
import time
import logging
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor
from jnpr.junos.exception import ConnectError
from week1_day6 import NetworkDevice


def setup_logging(log_file: str = "netauto.log") -> None:
    """Configure console + rotating file logging."""
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    # Console — INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File — DEBUG and above, rotates at 1MB, keeps 5 backups
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Root logger — accepts everything, handlers filter independently
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Suppress noisy libraries
    logging.getLogger("ncclient").setLevel(logging.CRITICAL)
    logging.getLogger("paramiko").setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)

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
        logger.error(f"Failed to connect to {device.host}: {e}")
        return {"hostname": device.host, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error for {device.host}: {e}")
        return {"hostname": device.host, "role": device.role, "error": f"Unexpected: {str(e)}"}


if __name__ == "__main__":
    setup_logging("netauto.log")
    logger.info("Starting concurrent inventory poll")
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
        NetworkDevice("10.49.0.254",  "CE", "labroot", "lab123"),#fake device to test error handling
        NetworkDevice("10.207.216.116",  "CE", "labroot", "lab123"),
    ]

    start = time.time()

    with ThreadPoolExecutor(max_workers=12) as executor:
        results = list(executor.map(poll_one_device, devices))

    end = time.time()

    for result in results:
        print(result)

    logger.info(f"Concurrent inventory collection completed in {end - start:.2f} seconds.")