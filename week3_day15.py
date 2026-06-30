from pybatfish.client.session import Session

bf = Session(host="localhost")

NETWORK_NAME = "lab_network"
SNAPSHOT_NAME = "week3_snapshot"
SNAPSHOT_PATH = "network_snapshot"

bf.set_network(NETWORK_NAME)
bf.init_snapshot(SNAPSHOT_PATH, name=SNAPSHOT_NAME, overwrite=True)

print("Snapshot loaded successfully!")

nodes = bf.q.nodeProperties().answer().frame()
print(nodes)

bgp_peers = bf.q.bgpPeerConfiguration().answer().frame()
print(bgp_peers)