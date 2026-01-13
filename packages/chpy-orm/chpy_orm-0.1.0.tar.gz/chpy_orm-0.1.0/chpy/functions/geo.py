"""
Geo functions for ClickHouse.
"""

from typing import Union
from chpy.orm import Column
from chpy.functions.base import Function


def greatCircleDistance(lat1: Union[Column, float], lon1: Union[Column, float],
                        lat2: Union[Column, float], lon2: Union[Column, float]) -> Function:
    """Great circle distance."""
    return Function("greatCircleDistance", lat1, lon1, lat2, lon2)


def geoDistance(lon1: Union[Column, float], lat1: Union[Column, float],
                lon2: Union[Column, float], lat2: Union[Column, float]) -> Function:
    """Geographic distance."""
    return Function("geoDistance", lon1, lat1, lon2, lat2)


def pointInPolygon(point: Union[Column, tuple], polygon: Union[Column, list]) -> Function:
    """Checks if point in polygon."""
    return Function("pointInPolygon", point, polygon)


def geohashEncode(latitude: Union[Column, float], longitude: Union[Column, float],
                  precision: int) -> Function:
    """Encodes to geohash."""
    return Function("geohashEncode", latitude, longitude, precision)


def geohashDecode(geohash_string: Union[Column, str]) -> Function:
    """Decodes geohash."""
    return Function("geohashDecode", geohash_string)


def geohashesInBox(lon_min: Union[Column, float], lat_min: Union[Column, float],
                   lon_max: Union[Column, float], lat_max: Union[Column, float],
                   precision: int) -> Function:
    """Geohashes in box."""
    return Function("geohashesInBox", lon_min, lat_min, lon_max, lat_max, precision)

