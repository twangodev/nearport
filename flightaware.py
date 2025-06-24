import os
from datetime import datetime

import requests
from dotenv import load_dotenv

from coordinates import bounding_box
from hexdb import get_icao24

load_dotenv()

API_TOKEN = os.getenv('FLIGHTAWARE_API_KEY')
BASE_URL = 'https://aeroapi.flightaware.com/aeroapi'
ENDPOINT = '/flights/search'

# Construct the full URL
url = f"{BASE_URL}{ENDPOINT}"

# Define the headers, including the Authorization header with your API token
headers = {
    'Accept': 'application/json',
    'x-apikey': API_TOKEN
}

CENTER = os.getenv("CENTER").split(",")
CENTER = (float(CENTER[0]), float(CENTER[1]))

RADIUS = os.getenv("RADIUS", 50)  # Default radius in nautical miles if not set

box = bounding_box(CENTER, RADIUS)
ne_bound = box['NE']
sw_bound = box['SW']
corners = (ne_bound[0], ne_bound[1], sw_bound[0], sw_bound[1])
bounds = " ".join(map(str, corners))

params = {
    'query': f'-latlong "{bounds}"'
}

def get_flight_positions():
    """
    Fetches live flight positions from the FlightAware AeroAPI.
    """

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching flight positions: {response.status_code} - {response.text}")

def to_positions(json):
    flights = json["flights"]

    positions = []

    for flight in flights:
        callsign = flight.get("ident")
        icao24 = get_icao24(callsign)

        last_position = flight.get("last_position")

        if not last_position:
            continue

        ts = last_position.get("timestamp")
        ts = datetime.fromisoformat(ts)
        ts = int(ts.timestamp())

        altitude = float(last_position.get("altitude")) * 100
        groundspeed = float(last_position.get("groundspeed"))

        heading = last_position.get("heading")
        heading = float(heading) if heading is not None else None

        latitude = float(last_position.get("latitude"))
        longitude = float(last_position.get("longitude"))

        position_update = {
            "icao24": icao24,
            "callsign": callsign,
            "altitude": altitude,
            "lat": latitude,
            "lon": longitude,
            "velocity": groundspeed,
            "heading": heading,
            "timestamp": ts
        }

        positions.append(position_update)

    return positions
