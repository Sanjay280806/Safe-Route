from __future__ import annotations

import math


EARTH_RADIUS_M = 6_371_000.0


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    )
    return 2.0 * EARTH_RADIUS_M * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def normalize_linestring_coordinates(raw: object) -> list[list[float]]:
    if not isinstance(raw, list):
        return []
    coords: list[list[float]] = []
    for item in raw:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            coords.append([float(item[0]), float(item[1])])
    return coords

