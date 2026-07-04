import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from jnpr.junos import device
from jnpr.junos.exception import ConnectError
from jnpr.junos.utils.config import CommitError, ConfigLoadError
from week1_day6 import NetworkDevice
import logging
logging.getLogger("paramiko").setLevel(logging.CRITICAL)
logging.getLogger("paramiko.transport").setLevel(logging.CRITICAL)


@dataclass
class DeployResult:
    host: str
    hostname: str
    success: bool
    diff: str | None = None
    error: str | None = None


def deploy_one_device(args: tuple) -> DeployResult:
    """
    Deploy config to one device with commit confirmed.
    Returns a DeployResult — always, never raises.

    Args:
        args: tuple of (NetworkDevice, config_text, confirm_minutes)
    """
    device, config_text, confirm_minutes = args
    try:
        device.connect()
        diff = device.deploy_confirmed(config_text, confirm_minutes)

        if not diff:
            device.disconnect()
            return DeployResult(
                host=device.host,
                hostname=device.host,
                success=True,
                diff=None,
                error="No changes needed"
            )
    except (ConnectError, ConfigLoadError, CommitError) as e:
        return DeployResult(
            host=device.host,
            hostname=device.host,
            success=False,
            error=str(e)
        )
    except Exception as e:
        return DeployResult(
            host=device.host,
            hostname=device.host,
            success=False,
            error=f"Unexpected: {str(e)}"
        )
    # verify — fresh RPC call AFTER commit, not reading from memory
    try:
        device.dev.rpc.get_system_information()  # fresh NETCONF round-trip
        hostname = device.facts.get("hostname", device.host)
        device.confirm_commit()
        device.disconnect()
        return DeployResult(
        host=device.host,
        hostname=hostname,
        success=True,
        diff=diff
    )
    except Exception as e:
        device.disconnect()
        return DeployResult(
        host=device.host,
        hostname=device.host,
        success=False,
        error=f"Post-commit verify failed — auto-rollback will occur: {e}"
    )

def print_deploy_report(results: list[DeployResult]) -> None:
    """Print a structured deployment report."""
    succeeded = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    print(f"\n{'='*60}")
    print(f"DEPLOYMENT REPORT")
    print(f"{'='*60}")
    print(f"Total: {len(results)} | Success: {len(succeeded)} | Failed: {len(failed)}")
    print(f"{'='*60}")

    if succeeded:
        print("\nSUCCESSFUL:")
        for r in succeeded:
            print(f"  ✓ {r.hostname} ({r.host})")
            if r.diff:
                print(f"    Changes applied: {r.diff[:80]}...")

    if failed:
        print("\nFAILED:")
        for r in failed:
            print(f"  ✗ {r.host}: {r.error}")


if __name__ == "__main__":
    # Safe test — just adding a description to unused interfaces
    # Using only PE devices for this test
    devices_and_configs = [
        (NetworkDevice("10.207.194.11",  "PE", "labroot", "lab123"),
         'set interfaces ge-0/0/9 unit 0 description "bulk-deploy-test-PE1"'),
        (NetworkDevice("10.207.194.94", "PE", "labroot", "lab123"),
         'set interfaces ge-0/0/9 unit 0 description "bulk-deploy-test-PE2"'),
        (NetworkDevice("10.207.195.43", "PE", "labroot", "lab123"),
         'set interfaces ge-0/0/9 unit 0 description "bulk-deploy-test-PE3"'),
    ]

    # Package as tuples for executor.map
    args = [(device, config, 2) for device, config in devices_and_configs]

    start = time.time()

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(deploy_one_device, args))

    end = time.time()

    print_deploy_report(results)
    print(f"\nBulk deployment completed in {end - start:.2f} seconds.")