from __future__ import annotations

ROAD_TYPE_ENCODE = {
    "footway": 0,
    "path": 0,
    "pedestrian": 0,
    "service": 1,
    "track": 1,
    "residential": 2,
    "unclassified": 2,
    "tertiary": 3,
    "secondary": 4,
    "primary": 5,
    "trunk": 6,
    "motorway": 6,
}

FEATURE_NAMES = [
    "length_m",
    "road_type_encoded",
    "is_underpass",
    "proximity_to_water",
    "drainage_proxy",
    "historical_flood_count",
]


def segment_features(segment) -> list[float]:
    return [
        float(getattr(segment, "length_m", 0.0) or 0.0),
        float(ROAD_TYPE_ENCODE.get(str(getattr(segment, "road_type", "unclassified")), 2)),
        1.0 if bool(getattr(segment, "is_underpass", False)) else 0.0,
        float(getattr(segment, "proximity_to_water", 0.5) or 0.5),
        float(getattr(segment, "drainage_proxy", 0.5) or 0.5),
        float(getattr(segment, "historical_flood_count", 0) or 0),
    ]

