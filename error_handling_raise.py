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
    except ConfigLoadError: # could use RpcError here, but ConfigLoadError object is more specific. Did you know that ConfigLoadError is a subclass of RpcError? So if you catch RpcError, you will also catch ConfigLoadError. But if you catch ConfigLoadError, you will not catch RpcError. So catching the more specific exception is better.
        cu.rollback()
        raise #Take the exception object we are currently sitting in, and keep throwing it upward.

    diff = cu.diff()

    try:
        cu.commit_check()
    except CommitError:
        cu.rollback()
        raise 

    cu.rollback()
    return diff


if __name__ == "__main__":
    HOST = "10.207.194.11"
    USER = "labroot"
    PASSWORD = "lab123"

    # deliberately bad config to test error handling
    config_text = "set interfaces ge-0/0/0 unit 0 family inet address 10.10.311.2/24"
    try:
        with Device(host=HOST, user=USER, password=PASSWORD) as dev:
            diff = push_config_dry_run(dev, config_text)
            print("Proposed change:")
            print(diff)
    except ConfigLoadError as main_block_Loaderror: #Catch the object that is currently flying through the air, and let me reference it using the variable name main_block_Loaderror.
        print(main_block_Loaderror)
    except CommitError as main_block_Commiterror:
        print(main_block_Commiterror)
    except ConnectError as main_block_Connecterror:
        print(main_block_Connecterror)