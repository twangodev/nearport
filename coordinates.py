import math

import geomag
from pyproj import Geod
from shapely import Point
from shapely.geometry import Polygon, mapping


def bounding_box(center, radius):
    """
    Returns a bounding box around a point (lat0, lon0)
    for a square centered at (lat0, lon0) with 'radius' in nm.
    """
    lat0, lon0 = center
    a = math.radians(lat0)

    dlat = radius / 60.0
    dlon = radius / (60.0 * math.cos(a))

    lat_min = lat0 - dlat
    lat_max = lat0 + dlat
    lon_min = lon0 - dlon
    lon_max = lon0 + dlon

    return {
        "SW": (lat_min, lon_min),
        "SE": (lat_min, lon_max),
        "NW": (lat_max, lon_min),
        "NE": (lat_max, lon_max),
    }

def true_to_magnetic(azimuth: float, lat: float, lon: float) -> float:
    decl = geomag.declination(lat, lon)
    return (azimuth - decl) % 360

def create_runoff_polygon_latlon(
        start: tuple[float, float],
        end: tuple[float, float],
        extension_miles: float,
        width_start_miles: float,
        width_end_miles: float,
) -> tuple[Polygon, float, dict]:
    """
    Build a 4-corner polygon that begins at the runway END and extends outward.
    Returns (polygon, true_heading, geojson).
    """
    geod = Geod(ellps="WGS84")

    # unpack lat/lon
    lat1, lon1 = start
    lat2, lon2 = end

    # true bearing from start→end
    az12, _, _ = geod.inv(lon1, lat1, lon2, lat2)

    # extension point beyond runway end
    ext_dist_m = extension_miles * 1609.34
    lon_ext, lat_ext, _ = geod.fwd(lon2, lat2, az12, ext_dist_m)

    # bearings perpendicular to runway heading
    left_bearing  = az12 - 90
    right_bearing = az12 + 90

    def offset(lat, lon, bearing, miles):
        d = miles * 1609.34
        lon_o, lat_o, _ = geod.fwd(lon, lat, bearing, d)
        return (lon_o, lat_o)

    bl = offset(lat2, lon2, left_bearing,  width_start_miles)
    br = offset(lat2, lon2, right_bearing, width_start_miles)

    fl = offset(lat_ext, lon_ext, left_bearing,  width_end_miles)
    fr = offset(lat_ext, lon_ext, right_bearing, width_end_miles)

    poly    = Polygon([bl, br, fr, fl])
    geojson = mapping(poly)

    return poly, true_to_magnetic(az12, lat1, lon1), geojson

def classify_to_la(
        lat: float,
        lon: float,
        aircraft_heading: float,
        runway_extensions: list[tuple[str, Polygon, float, dict]],
) -> tuple[str, str] | None:
    """
    Returns:
      - "TO" if the aircraft is inside one of the runway-extension polygons
        and its heading is closer to the runway's forward bearing.
      - "LA" if inside but heading is closer to runway_bearing + 180°.
      - None if it's not in any polygon.
    """
    pt = Point(lon, lat)
    # normalize heading to [0,360)
    hdg = aircraft_heading % 360

    def angle_diff(a: float, b: float) -> float:
        """Minimum difference between two headings in degrees."""
        return abs((a - b + 180) % 360 - 180)

    for name, poly, runway_hdg, _ in runway_extensions:
        if poly.contains(pt):
            # forward vs. opposite
            fwd = runway_hdg % 360
            back = (fwd + 180) % 360

            runway_names = name.split("-")
            if angle_diff(hdg, fwd) < angle_diff(hdg, back):
                return runway_names[0], "TO"
            else:
                return runway_names[1], "LA"
    return None