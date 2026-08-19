from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    id: int
    lat: float
    lon: float


@dataclass
class RoadSegment:
    id: int
    from_node_id: int
    to_node_id: int
    length_m: float
    geometry: list[list[float]]
    name: str = "Unnamed road"
    road_type: str = "unclassified"
    is_underpass: bool = False
    low_lying_prior: float = 0.35
    proximity_to_water: float = 0.5
    drainage_proxy: float = 0.5
    historical_flood_count: int = 0
    ml_static_propensity: float | None = None
    blocked: bool = False
    flood_status: str = "safe"


@dataclass(frozen=True)
class Scenario:
    id: int
    name: str
    rainfall_mm_24h: float
    rainfall_mm_1h: float
    is_active: bool = False


@dataclass(frozen=True)
class Poi:
    id: int
    name: str
    category: str
    lat: float
    lon: float
    nearest_node_id: int | None = None
    status: str = "open"


@dataclass(frozen=True)
class SegmentRisk:
    segment_id: int
    risk_score: float
    risk_level: str
    predicted_time_to_high_risk_min: float | None


@dataclass(frozen=True)
class PathResult:
    route_type: str
    segment_ids: list[int]
    node_ids: list[int]
    distance_m: float
    duration_min: float
    cost_score: float
    avg_risk_score: float
    high_risk_segments_count: int
    blocked_segments_encountered: int
    geometry: list[list[float]]

