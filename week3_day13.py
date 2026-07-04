from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError


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
    cu.load(config_text, format="set")
    diff = cu.diff()
    cu.commit_check()
    cu.rollback()  # discard the staged change — pure dry run
    return diff


if __name__ == "__main__":
    HOST = "10.207.194.11"
    USER = "labroot"
    PASSWORD = "lab123"

    config_text = 'set interfaces ge-0/0/0 unit 0 description "Link to PE2 - TEST"'

    try:
        with Device(host=HOST, user=USER, password=PASSWORD) as dev:
            diff = push_config_dry_run(dev, config_text)
            print("Proposed change:")
            print(diff)
    except ConnectError as e:
        print(f"Connection failed: {e}")