import logging
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.op.ethport import EthPortTable
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConfigLoadError, CommitError

logger = logging.getLogger(__name__)

class NetworkDevice:
    
    def __init__(self, host: str, role: str, user: str, password: str):
        # __init__ is the constructor — runs when object is created
        self.host = host        # attribute
        self.role = role        # attribute
        self.user = user        # attribute
        self.password = password # attribute
        self.facts = {}         # empty for now — populated on connect
    
    def __enter__(self):
        """
        Allows NetworkDevice to be used with 'with' statement.
        Automatically calls connect() when entering the block.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Automatically calls disconnect() when exiting the block,
        even if an exception occurred inside.
        """
        self.disconnect()

    def connect(self) -> None:
        # method — action the object can perform
        try:
            self.dev=Device(host=self.host, user=self.user, password=self.password)
            self.dev.open()
            self.facts = self.dev.facts
        except ConnectError as e:
            raise # re-raise the exception so the caller knows connection failed
    def disconnect(self) -> None:
        # method — action the object can perform
        self.dev.close()
    def get_summary(self) -> dict:
        # method — returns data
        return {
        "hostname": self.facts["hostname"],
        "role": self.role,
        "model": self.facts["model"],
        "version": self.facts["version"],
        "uptime": self.facts["RE0"]["up_time"],
    }
    def get_interfaces(self) -> list[dict]:
        """
        Fetch interface operational status.

        Returns:
        List of dicts with name, oper, admin status
        """
        eth_table = EthPortTable(self.dev)
        eth_table.get()
        return [{"name": intf.name, "oper": intf.oper, "admin": intf.admin} for intf in eth_table]
    def get_bgp_neighbors(self) -> list[dict]:
        """
        Fetch BGP neighbor status using direct RPC call.

        Returns:
            List of dicts with peer address and state
        """
        result = self.dev.rpc.get_bgp_summary_information()
        peers = result.findall(".//bgp-peer")
        return [
            {
                "peer": peer.find("peer-address").text,
                "state": peer.find("peer-state").text,
            }
            for peer in peers
        ]
    def deploy_dry_run(self, config_text: str) -> str | None:
        """
        Load config, validate, show diff, then ALWAYS rollback — never commits.

        Args:
        config_text: Junos set-style config as a string

        Returns:
        The configuration diff, or None if no changes
        """
        cu = Config(self.dev)
        cu.load(config_text, format="set")
        diff = cu.diff()

        if not diff:
            cu.rollback()
            return None

        cu.commit_check()
        cu.rollback()
        return diff
    def deploy_confirmed(self, config_text: str, confirm_minutes: int = 1) -> str | None:
        """
        Load config and commit with a confirm timer — auto-reverts if not confirmed.

        Args:
        config_text: Junos set-style config as a string
        confirm_minutes: Minutes before auto-rollback if not confirmed

        Returns:
        The diff that was committed, or None if no changes
        """
        cu = Config(self.dev)
        cu.load(config_text, format="set")
        diff = cu.diff()

        if not diff:
            cu.rollback()
            return None

        cu.commit_check()
        cu.commit(confirm=confirm_minutes)
        return diff

    def confirm_commit(self) -> None:
        """
        Confirm a pending commit-confirmed, making it permanent.
        """
        cu = Config(self.dev)
        cu.commit()
    def get_interface_addresses(self, interface_name: str) -> list[str]:
        """
        Get currently configured IPv4 addresses on a specific interface.

        Args:
        interface_name: Interface name e.g. ge-0/0/0

        Returns:
        List of configured addresses (CIDR format), empty if none
        """
        result = self.dev.rpc.get_config(filter_xml=f"<configuration><interfaces><interface><name>{interface_name}</name></interface></interfaces></configuration>")
        addresses = result.findall(".//address/name")
        return [addr.text for addr in addresses]
if __name__ == "__main__":
    with NetworkDevice(host="10.207.194.11",role="PE",user="labroot",password="lab123") as pe1:
        print(pe1.get_summary())
        print(pe1.get_interfaces())
        print(pe1.get_bgp_neighbors())
        config_text = 'set interfaces ge-0/0/9 unit 0 description "TEST - commit confirmed"'
        diff = pe1.deploy_confirmed(config_text, confirm_minutes=1)
        print("Committed with confirm timer:")
        print(diff)