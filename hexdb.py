import requests

# Create a single Session for all requests
_session = requests.Session()

def get_icao24(callsign: str) -> str | None:
    """
    Converts a callsign to an ICAO24 address using a persistent session.
    """
    url = f"https://hexdb.io/reg-hex?reg={callsign}"
    response = _session.get(url)
    if response.status_code == 200:
        return response.text.strip()
    return None
