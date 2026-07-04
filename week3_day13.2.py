from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError, CommitError, ConfigLoadError


def push_config_dry_run(dev: Device, config_text: str) -> str:
    """
    Load config and show diff WITHOUT committing.

    Args:
        dev: Connected PyEZ Device object
        config_text: Junos set-style config as a string

    Returns:
        The configuration diff
    """
    cu = Config(dev)

    try:
        cu.load(config_text, format="set")
    except ConfigLoadError as e:
        cu.rollback()
        raise

    diff = cu.diff()

    try:
        cu.commit_check()
    except CommitError as e:
        cu.rollback()
        raise 

    cu.rollback()
    return diff


if __name__ == "__main__":
    HOST = "10.207.194.11"
    USER = "labroot"
    PASSWORD = "lab123"

    # deliberately bad config to test error handling
    config_text = "set interfaces ge-0/0/0 unit 0 family inet address 10.10.11.2/24\nset interfaces ge-0/0/0 unit 0 family bridge"
    try:
        with Device(host=HOST, user=USER, password=PASSWORD) as dev:
            diff = push_config_dry_run(dev, config_text)
            print("Proposed change:")
            print(diff)
    except ConfigLoadError as e:
        print("Config syntax was invalid — fix the template")
    except CommitError as e:
        print("Config syntax was fine, but values were invalid — check IPs/parameters")
    except ConnectError as e:
        print(f"Connection failed: {e}")