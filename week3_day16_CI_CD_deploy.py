import yaml
from jinja2 import Template
from week3_day12 import load_interfaces
from jnpr.junos.utils.config import CommitError, Config, ConfigLoadError
from jnpr.junos.exception import ConnectError
from jnpr.junos import Device

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

def test_stage(config_commands: list[str]) -> bool:
    """Stage 3: Validate config logic (placeholder for Batfish integration)."""
    print("=== TEST STAGE ===")
    if not config_commands:
        print("No config commands to test.")
        return False
    print (f"Testing {len(config_commands)} config commands...")
    for cmd in config_commands:
        print(f"Testing command: {cmd}")
    return True

def deploy_stage_confirmed(host: str, user: str, password: str, config_commands: list[str]) -> bool:
    """
    Deploy stage using commit confirmed — real commit, but auto-reverts
    if not confirmed within the timer window.
    """
    print("=== DEPLOY STAGE (commit confirmed) ===")
    full_config = "\n".join(config_commands)
    try:
        with Device(host=host, user=user, password=password) as dev:
            cu = Config(dev)
            cu.load(full_config, format="set")
            diff = cu.diff()
            print("Proposed changes:")
            print(diff if diff else "No changes detected")

            if not diff:
                cu.rollback()
                return True  # nothing to commit, not a failure

            cu.commit_check()
            cu.commit(confirm=1)  # commits now, auto-reverts in 1 minute unless confirmed
            print("Committed with 1-minute confirm timer running...")
        # Verify stage — reuse the same open connection
            print("=== VERIFY STAGE ===")
            dev.facts_refresh()  # refresh facts to check if device is still reachable
            if dev.facts["hostname"]:
                print(f"Device {dev.facts['hostname']} still reachable — confirming commit")
                cu.commit()  # plain commit = confirms, cancels the rollback timer
                print("Commit confirmed permanently")
                return True
            else:
                print("Verify failed — not confirming, Junos will auto-rollback")
                return False
    except (ConfigLoadError, CommitError) as e:
        print(f"Deploy failed validation: {e}")
        return False
    except ConnectError as e:
        print(f"Connection failed: {e}")
        return False
if __name__ == "__main__":
    host = "10.207.194.11"
    user = "labroot"
    password = "lab123"
    YAML_PATH = "interfaces.yaml"

    if not lint_stage(YAML_PATH):
        print("\nPipeline FAILED at stage: Lint")
    else:
        config_commands = build_stage(YAML_PATH)
        if not config_commands:
            print("\nPipeline FAILED at stage: Build")
        elif not test_stage(config_commands):
            print("\nPipeline FAILED at stage: Test")
        elif not deploy_stage_confirmed(host, user, password, config_commands):
            print("\nPipeline FAILED at stage: Deploy")
        else:
            print("\nCommit Confirmed Pipeline completed successfully!")
