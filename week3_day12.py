import yaml
from jinja2 import Template

INTERFACE_TEMPLATE = Template("""\
set interfaces {{ interface }} unit 0 description "{{ description }}"
set interfaces {{ interface }} unit 0 family inet address {{ ip_address }}
""")


def load_interfaces(filepath: str) -> list[dict]:
    """
    Load interface data from a YAML source of truth file.

    Args:
        filepath: Path to the YAML file

    Returns:
        List of interface dictionaries
    """
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    return data["interfaces"]


if __name__ == "__main__":
    interfaces = load_interfaces("interfaces.yaml")
    for interface in interfaces:
        config = INTERFACE_TEMPLATE.render(
            interface=interface["name"],
            description=interface["description"],
            ip_address=interface["ip_address"],
        )
        print(config)