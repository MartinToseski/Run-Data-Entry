"""
Geospatial helper logic for country detection and trip inference.
"""

from typing import List, Tuple
from shapely.geometry import Point
from config import WORLD


def coordinates_to_country(coords: List[tuple]) -> List[str]:
    """
    Convert latitude/longitude coordinates to country names.
    Parameters:
        coords: List of (latitude, longitude) tuples.
    Returns:
        List of detected country names. May be empty if no match.
    """
    if WORLD is None or not coords:
        return []

    country_list = []
    for lat, lon in coords:
        try:
            point = Point(lon, lat)
            match = WORLD[WORLD.geometry.apply(lambda geom: point.within(geom))]

            if not match.empty:
                country_list.append(match.iloc[0]["ADMIN"])
        except Exception:
            continue

    return country_list


def find_trip(country_list: List[str]) -> bool:
    """
    Determine whether multiple unique countries appear in the list.
    Used to infer potential travel in the analysis window.
    """
    return len(set(country_list)) > 1