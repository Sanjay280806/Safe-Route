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


def lon_lat_key(lon: float, lat: float) -> str:
    return f"{lon:.7f}_{lat:.7f}"


def line_length_m(coordinates: list[list[float]]) -> float:
    total = 0.0
    for index in range(1, len(coordinates)):
        lon1, lat1 = coordinates[index - 1]
        lon2, lat2 = coordinates[index]
        total += haversine_m(lat1, lon1, lat2, lon2)
    return total


def segment_midpoint(coordinates: list[list[float]]) -> tuple[float, float]:
    if not coordinates:
        return (0.0, 0.0)
    mid = coordinates[len(coordinates) // 2]
    return (float(mid[1]), float(mid[0]))


def risk_level_for_score(score: float) -> str:
    if score < 0.25:
        return "low"
    if score < 0.50:
        return "moderate"
    if score < 0.75:
        return "high"
    return "critical"

