from jnpr.junos import Device

with Device(host="10.49.0.137", user="labroot", password="lab123") as dev:
    result = dev.rpc.get_bgp_summary_information()
    
    peers = result.findall(".//bgp-peer")
    for peer in peers:
        address = peer.find("peer-address").text
        state = peer.find("peer-state").text
        print(f"Peer: {address} | State: {state}")

