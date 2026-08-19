from typing import Any, Literal

from pydantic import BaseModel, Field


class LatLon(BaseModel):
    lat: float
    lon: float


class Destination(BaseModel):
    poi_id: int | None = None
    lat: float | None = None
    lon: float | None = None


class RouteRequest(BaseModel):
    origin: LatLon
    destination: Destination
    route_mode: Literal["safe", "short", "compare"] = "safe"
    scenario_id: int | None = None
    include_alternatives: bool = True


class RerouteRequest(BaseModel):
    current_location: LatLon
    destination: Destination
    reason: str = "blocked_ahead"
    route_mode: Literal["safe", "short", "compare"] = "safe"
    scenario_id: int | None = None
    include_alternatives: bool = True


class GeoJSONLineString(BaseModel):
    type: Literal["LineString"] = "LineString"
    coordinates: list[list[float]] = Field(default_factory=list)


class RouteObject(BaseModel):
    route_type: Literal["safe", "short"]
    distance_m: float
    duration_min: float
    cost_score: float
    avg_risk_score: float
    high_risk_segments_count: int
    blocked_segments_encountered: int
    predicted_risk_warnings_count: int
    geometry: GeoJSONLineString


class RouteWarning(BaseModel):
    warning_type: str
    segment_id: int
    road_name: str
    eta_to_segment_min: float
    predicted_time_to_high_risk_min: float | None
    message: str


class RouteExplanation(BaseModel):
    safe_route_adds_min: float
    high_risk_segments_avoided: int
    blocked_segments_avoided: int
    summary: str


class RouteResponse(BaseModel):
    request_id: int
    destination: dict[str, Any]
    routes: list[RouteObject]
    warnings: list[RouteWarning]
    explanation: RouteExplanation
