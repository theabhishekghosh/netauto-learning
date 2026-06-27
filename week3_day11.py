from jinja2 import Template

INTERFACE_TEMPLATE = Template("""\
set interfaces {{ interface }} unit 0 description "{{ description }}"
set interfaces {{ interface }} unit 0 family inet address {{ ip_address }}
""")

if __name__ == "__main__":
    interfaces = [
        {"name": "ge-0/0/0", "description": "Link to PE2", "ip_address": "10.1.1.1/30"},
        {"name": "ge-0/0/1", "description": "Link to CE1", "ip_address": "10.1.1.5/30"},
        {"name": "ge-0/0/2", "description": "Link to P4", "ip_address": "10.1.1.9/30"},
    ]
    for interface in interfaces:
        config = INTERFACE_TEMPLATE.render(
            interface=interface["name"],
            description=interface["description"],
            ip_address=interface["ip_address"],
        )
        print(config)