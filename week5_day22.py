import requests

def get_ip_info(ip_address: str) -> dict:
    """
    Get geolocation info for an IP address.

    Args:
        ip_address: IP address to look up

    Returns:
        Dictionary with location information
    """
    response = requests.get(f"http://ip-api.com/json/{ip_address}", allow_redirects=False)
    response.raise_for_status()
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    return response.json()


if __name__ == "__main__":
    result = get_ip_info("8.8.8.8")
    print(result)

if __name__ == "__main__":
    ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
    
    for ip in ips:
        result = get_ip_info(ip)
        print(f"{ip:20} {result.get('org', 'unknown'):40} {result.get('country', 'unknown')}")