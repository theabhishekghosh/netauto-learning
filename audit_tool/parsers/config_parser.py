# audit_tool/parsers/config_parser.py
from logging import config
import re
import logging

from pyparsing import line

logger = logging.getLogger(__name__)


def parse_set_format(config_text: str) -> dict:
    """
    Parse Junos 'show configuration | display set' format.
    Input must be pure display set format — one 'set' line per statement.

    Args:
        config_text: Raw text from 'show configuration | display set | no-more'

    Returns:
        Structured configuration dictionary
    """
    config = {
        "hostname": None,
        "bgp": {"groups": {}},
        "ospf": {"areas": {}},
        "mpls": {"interfaces": []},
        "interfaces": {},
        "rsvp": {"enabled": False},
        "routing_options": {
            "router_id": None,
            "autonomous_system": None
        }
    }

    for line in config_text.splitlines():
        line = line.strip()

        # skip empty lines, comments, version line, non-set lines
        if not line or not line.startswith("set "):
            continue

        # hostname — from groups re0
        m = re.match(r"set groups re0 system host-name (\S+)", line)
        if m:
            config["hostname"] = m.group(1)
            continue

        # router-id
        m = re.match(r"set routing-options router-id (\S+)", line)
        if m:
            config["routing_options"]["router_id"] = m.group(1)
            continue

        # autonomous-system
        m = re.match(r"set routing-options autonomous-system (\S+)", line)
        if m:
            config["routing_options"]["autonomous_system"] = m.group(1)
            continue

        # BGP group export policy
        m = re.match(r"set protocols bgp group (\S+) export (\S+)", line)
        if m:
            group, policy = m.group(1), m.group(2)
            if group not in config["bgp"]["groups"]:
                config["bgp"]["groups"][group] = {
                    "export_policies": [],
                    "neighbors": []
                }
            config["bgp"]["groups"][group]["export_policies"].append(policy)
            continue

        # BGP group neighbor — match only the neighbor IP, not sub-attributes
        m = re.match(r"set protocols bgp group (\S+) neighbor (\d+\.\d+\.\d+\.\d+)\s", line)
        if m:
            group, neighbor = m.group(1), m.group(2)
            if group not in config["bgp"]["groups"]:
                config["bgp"]["groups"][group] = {
                    "export_policies": [],
                    "neighbors": []
                }
            if neighbor not in config["bgp"]["groups"][group]["neighbors"]:
                config["bgp"]["groups"][group]["neighbors"].append(neighbor)
            continue
        # Add this pattern — catches any BGP group line and ensures group exists:
        m = re.match(r"set protocols bgp group (\S+)", line)
        if m:
            group = m.group(1)
            if group not in config["bgp"]["groups"]:
                config["bgp"]["groups"][group] = {
                    "export_policies": [],
                    "neighbors": []
                }

        # OSPF interface
        m = re.match(r"set protocols ospf area (\S+) interface (\S+)", line)
        if m:
            area, intf = m.group(1), m.group(2)
            if area not in config["ospf"]["areas"]:
                config["ospf"]["areas"][area] = {"interfaces": []}
            if intf not in config["ospf"]["areas"][area]["interfaces"]:
                config["ospf"]["areas"][area]["interfaces"].append(intf)
            continue

        # MPLS interface
        m = re.match(r"set protocols mpls interface (\S+)", line)
        if m:
            intf = m.group(1)
            if intf not in config["mpls"]["interfaces"]:
                config["mpls"]["interfaces"].append(intf)
            continue

        # RSVP
        if re.match(r"set protocols rsvp", line):
            config["rsvp"]["enabled"] = True
            continue

        # Interface address — match before family to be more specific
        m = re.match(r"set interfaces (\S+) unit (\d+) family inet address (\S+)", line)
        if m:
            intf, unit, addr = m.group(1), m.group(2), m.group(3)
            intf_key = f"{intf}.{unit}"
            if intf_key not in config["interfaces"]:
                config["interfaces"][intf_key] = {"families": [], "address": None}
            config["interfaces"][intf_key]["address"] = addr
            continue

        # Interface family
        m = re.match(r"set interfaces (\S+) unit (\d+) family (\S+)", line)
        if m:
            intf, unit, family = m.group(1), m.group(2), m.group(3)
            intf_key = f"{intf}.{unit}"
            if intf_key not in config["interfaces"]:
                config["interfaces"][intf_key] = {"families": [], "address": None}
            if family not in config["interfaces"][intf_key]["families"]:
                config["interfaces"][intf_key]["families"].append(family)

    return config


def load_device_config(filepath: str) -> dict:
    """
    Load and parse a device config file.

    Args:
        filepath: Path to the config file

    Returns:
        Parsed config dict, empty dict if file not found or parse error
    """
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            content = f.read()
        logger.info(f"Loaded config from {filepath}")
        return parse_set_format(content)
    except FileNotFoundError:
        logger.error(f"Config file not found: {filepath}")
        return {}
    except Exception as e:
        logger.error(f"Failed to parse {filepath}: {e}")
        return {}