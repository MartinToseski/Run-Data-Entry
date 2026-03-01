"""
Global configuration and shared constants.
"""

import os
import logging
import geopandas as gpd


# Suppress verbose garminconnect logging
logging.getLogger("garminconnect").setLevel(logging.CRITICAL)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHAPEFILE_PATH = os.path.join(BASE_DIR, "..", "..", "data", "ne_110m_admin_0_countries", "ne_110m_admin_0_countries.shp")


# ---------------------------------------------------------------------
# Geospatial Data
# ---------------------------------------------------------------------
try:
    WORLD = gpd.read_file(SHAPEFILE_PATH)
except Exception as e:
    print("World shapefile could not be loaded:", e)
    WORLD = None


# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------
DAYS_OF_THE_WEEK = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}