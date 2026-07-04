import yaml
from jinja2 import Template
from week3_day12 import load_interfaces
from jnpr.junos.utils.config import CommitError, Config, ConfigLoadError
from jnpr.junos.exception import ConnectError
from week1_day6 import NetworkDevice

def lint_stage(yaml_path: str) -> bool:
    """Stage 1: Validate YAML source of truth is well-formed."""
    print("=== LINT STAGE ===")
    try:
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"YAML error: {e}")
        return False
    if not data:
        print("YAML file is empty or invalid.")
        return False
    if "interfaces" not in data:
        print("YAML file missing 'interfaces' key.")
        return False
    for interface in data["interfaces"]:
        print(f"YAML is valid for interface: {interface['name']}")
    return True

def build_stage(yaml_path: str) -> list[str]:
    """Stage 2: Render Jinja2 templates into Junos config commands."""
    print("=== BUILD STAGE ===")
    INTERFACE_TEMPLATE = Template(
        'set interfaces {{ interface }} unit 0 description "{{ description }}"\n'
        'set interfaces {{ interface }} unit 0 family inet address {{ ip_address }}'
    )
    interfaces = load_interfaces(yaml_path)
    config_commands = []
    for interface in interfaces:
        config = INTERFACE_TEMPLATE.render(
            interface=interface["name"],
            description=interface["description"],
            ip_address=interface["ip_address"],
        )
        config_commands.append(config)
        print(config)
    return config_commands
def check_existing_config(host: str, role: str, user: str, password: str, interfaces: list[dict]) -> bool:
    """
    Pre-flight check: verify no interface already has a DIFFERENT address configured.

    Args:
        host, role, user, password: device connection details
        interfaces: list of dicts with name, ip_address (from YAML)

    Returns:
        True if safe to proceed, False if a conflict is found
    """
    print("=== PRE-FLIGHT CHECK ===")
    conflicts_found = False
    with NetworkDevice(host, role, user, password) as device:
        for interface in interfaces:
            existing = device.get_interface_addresses(interface["name"])
            intended = interface["ip_address"]
            if existing and intended not in existing:
                print(f"CONFLICT on {interface['name']}: existing={existing}, intended={intended}")
                conflicts_found = True
            else:
                print(f"OK: {interface['name']} — no conflict")
    return not conflicts_found

def test_stage(config_commands: list[str]) -> bool:
    """Stage 3: Validate config logic (placeholder for Batfish integration)."""
    print("=== TEST STAGE ===")
    if not config_commands:
        print("No config commands to test.")
        return False
    print (f"Testing {len(config_commands)} config commands...")
    for cmd in config_commands:
        print(f"Testing command: {cmd}")
    return True  # Placeholder for actual test logic


def deploy_stage(host: str, role: str, user: str, password: str, config_commands: list[str]) -> bool:
    """Stage 4: Push config via NetworkDevice, dry-run only (commit_check + rollback)."""
    print("=== DEPLOY STAGE ===")
    full_config = "\n".join(config_commands)
    try:
        with NetworkDevice(host, role, user, password) as device:
            diff = device.deploy_dry_run(full_config)
            print("Proposed change:")
            print(diff if diff else "No changes proposed.")
            return True
    except ConfigLoadError as e:
        print("Config syntax was invalid — fix the template")
        return False
    except CommitError as e:
        print("Config syntax was fine, but values were invalid — check IPs/parameters")
        return False
    except ConnectError as e:
        print(f"Connection failed: {e}")
        return False

def verify_stage(host: str, user: str,role: str,password: str) -> bool:
    """Stage 5: Confirm device state after deployment."""
    print("=== VERIFY STAGE ===")
    try:
        with NetworkDevice(host=host, user=user, role=role, password=password) as dev:
            summary = dev.get_summary()
            print(f"Device summary: {summary}") 
            return True
    except ConnectError as e:
            print(f"Verification failed: {e}")
            return False

if __name__ == "__main__":
    host = "10.207.194.11"
    user = "labroot"
    role = "PE"
    password = "lab123"
    YAML_PATH = "interfaces.yaml"

    if not lint_stage(YAML_PATH):
        print("\nPipeline FAILED at stage: Lint")
    else:
        config_commands = build_stage(YAML_PATH)
        if not config_commands:
            print("\nPipeline FAILED at stage: Build")
        else:
            interfaces = load_interfaces(YAML_PATH)
        if not check_existing_config(host, role, user, password, interfaces):
            print("\nPipeline FAILED at stage: Pre-flight check")
        elif not test_stage(config_commands):
            print("\nPipeline FAILED at stage: Test")
        elif not deploy_stage(host, role, user, password, config_commands):
            print("\nPipeline FAILED at stage: Deploy")
        elif not verify_stage(host, user, role, password):
            print("\nPipeline FAILED at stage: Verify")
        else:
            print("\nVerification Pipeline completed successfully!")
