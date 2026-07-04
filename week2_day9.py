from week1_day6 import NetworkDevice


def find_down_bgp_peers(peers: list[dict]) -> list[dict]:
    """
    Find BGP peers not in Established state.

    Args:
        peers: List of dicts with peer and state

    Returns:
        List of peers that are down
    """
    return [peer for peer in peers if peer["state"] != "Established"]


if __name__ == "__main__":
    pe1 = NetworkDevice("10.207.194.11", "PE", "labroot", "lab123")
    pe1.connect()

    peers = pe1.get_bgp_neighbors()
    for peer in peers:
        print(peer)

    down_peers = find_down_bgp_peers(peers)
    print(f"\n{len(down_peers)} BGP peers not Established:")
    for p in down_peers:
        print(f"  {p['peer']} - {p['state']}")

    pe1.disconnect()