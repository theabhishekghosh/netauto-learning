import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

def connect_device(host: str) -> bool:
    """Simulate connecting to a device."""
    logger.info(f"Attempting connection to {host}")
    if host == "10.49.0.254":
        logger.error(f"Failed to connect to {host} — host unreachable")
        return False
    logger.info(f"Successfully connected to {host}")
    return True

def poll_device(host: str) -> None:
    """Simulate polling a device."""
    logger.debug(f"Starting poll for {host}")
    connected = connect_device(host)
    if not connected:
        logger.warning(f"Skipping {host} — connection failed")
        return
    logger.debug(f"Poll complete for {host}")

if __name__ == "__main__":
    hosts = ["10.207.194.11", "10.49.0.254", "10.207.194.94"]
    for host in hosts:
        poll_device(host)