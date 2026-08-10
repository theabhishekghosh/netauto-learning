from aos.sdk.api import TwoStageL3ClosClient
from collections import Counter

client = TwoStageL3ClosClient(
    "https://10.52.137.219/api",
    verify_certificates=False,
)
client.login("admin", "Qazwsxedcrfv@123")

bp = client.blueprints["521b38c2-996d-4844-93f2-d3fcd1666fdd"]

nodes = bp.nodes.list()
print(type(nodes))

type_counts = Counter(v.get("type") for v in nodes.values())
for node_type, count in sorted(type_counts.items()):
    print(node_type, count)

print("---")

systems = {k: v for k, v in nodes.items() if v.get("type") == "system"}
for node_id, sysnode in systems.items():
    print(node_id, "|", sysnode.get("role"), "|", sysnode.get("label"), "|", sysnode.get("hostname"))

rg = {k: v for k, v in nodes.items() if v.get("type") == "redundancy_group"}
for node_id, rgnode in rg.items():
    print(node_id, "|", rgnode)

print("---")

leaf_ids = ["R8m8claMx4Y09aJUVA", "DzPKFm1Xhp9v2Lr7fA"]
for lid in leaf_ids:
    print(lid, "|", nodes[lid])