"""
Internal helpers for pyasyncspeedtest.

This module is private and not part of the public API.
All functions and classes here may change without notice.
"""

import math
import aiohttp
from typing import Optional


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two geographic coordinates using Haversine formula.

    Args:
        lat1: Latitude of the first coordinate
        lon1: Longitude of the first coordinate
        lat2: Latitude of the second coordinate
        lon2: Longitude of the second coordinate

    Returns:
        Distance in kilometers
    """
    R = 6371  # Radius of the earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


def create_connector(source_address: Optional[str] = None) -> Optional[aiohttp.TCPConnector]:
    """
    Create a TCPConnector with optional source address binding.

    Args:
        source_address: IP address to bind to

    Returns:
        TCPConnector if source_address provided, else None
    """
    if source_address:
        return aiohttp.TCPConnector(local_addr=(source_address, 0))
    return None
