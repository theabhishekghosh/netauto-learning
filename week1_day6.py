from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.op.ethport import EthPortTable

class NetworkDevice:
    
    def __init__(self, host: str, role: str, user: str, password: str):
        # __init__ is the constructor — runs when object is created
        self.host = host        # attribute
        self.role = role        # attribute
        self.user = user        # attribute
        self.password = password # attribute
        self.facts = {}         # empty for now — populated on connect
    
    def connect(self) -> None:
        # method — action the object can perform
        try:
            self.dev=Device(host=self.host, user=self.user, password=self.password)
            self.dev.open()
            self.facts = self.dev.facts
        except ConnectError as e:
            print(f"Error connecting to device {self.host}: {e}")
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
if __name__ == "__main__":
    pe1 = NetworkDevice(
        host="10.49.0.137",
        role="PE",
        user="labroot",
        password="lab123"
    )
    pe1.connect()
    print(pe1.get_summary())
    print(pe1.get_interfaces())
    print(pe1.get_bgp_neighbors())
    pe1.disconnect()