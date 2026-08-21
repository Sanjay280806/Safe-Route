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


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorBody


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    active_scenario_id: int | None
    road_count: int
    poi_count: int


class AreaMetaResponse(BaseModel):
    name: str
    bbox: list[float]
    default_center: list[float]
    default_zoom: int
    disclaimer: str


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class AuthUser(BaseModel):
    id: int
    username: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: AuthUser


class ScenarioResponse(BaseModel):
    id: int
    name: str
    description: str | None
    rainfall_mm_24h: float
    rainfall_mm_1h: float
    source: str
    is_active: bool


class PoiResponse(BaseModel):
    id: int
    external_id: str | None
    name: str
    category: str
    lat: float
    lon: float
    address: str | None
    phone: str | None
    status: str
    nearest_node_id: int | None
    source: str
    notes: str | None


class BlockedReportRequest(BaseModel):
    segment_id: int
    source: str = "field_official"
    note: str | None = Field(default=None, max_length=500)
    flood_status: str = "confirmed_flooded"


class RoadStatus(BaseModel):
    blocked: bool
    flood_status: str
    current_risk_level: str


class BlockedReportResponse(BaseModel):
    report_id: int
    segment_id: int
    verification_status: str
    credibility_score: float
    road_status: RoadStatus


class VerifyReportRequest(BaseModel):
    decision: Literal["confirm", "reject"]


class ActiveReportResponse(BaseModel):
    id: int
    segment_id: int
    road_name: str | None
    source: str
    verification_status: str
    note: str | None
    created_at: str


class ValidationSegment(BaseModel):
    segment_id: int
    name: str
    risk_score: float
    risk_level: str


class ValidationSummaryResponse(BaseModel):
    model_loaded: bool
    model_type: str
    segment_count: int
    risk_distribution: dict[str, int]
    top_high_risk_segments: list[ValidationSegment]
    documented_flood_pockets: list[str]


class RecomputeRiskResponse(BaseModel):
    scenario_id: int
    segments_updated: int
    model_loaded: bool


class RainfallUpdateRequest(BaseModel):
    rainfall_mm_24h: float = Field(ge=0, le=500)
    rainfall_mm_1h: float = Field(ge=0, le=200)
    description: str | None = Field(default=None, max_length=300)


class RainfallResponse(BaseModel):
    scenario_id: int
    scenario_name: str
    rainfall_mm_24h: float
    rainfall_mm_1h: float
    source: str
    updated_from: str


class ShelterResponse(BaseModel):
    poi_id: int
    name: str
    lat: float
    lon: float
    address: str | None
    status: str
    capacity_assumed: int
    occupancy_assumed: int
    available_capacity: int
    accessible: bool
    medical_support: bool
    water_available: bool
    source: str
    notes: str | None


class ShelterOccupancyUpdateRequest(BaseModel):
    occupancy_assumed: int = Field(ge=0, le=100000)
    status: str | None = Field(default=None, max_length=32)


class ShelterCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    address: str | None = Field(default=None, max_length=255)
    capacity_assumed: int = Field(ge=1, le=100000)
    occupancy_assumed: int = Field(default=0, ge=0, le=100000)
    accessible: bool = False
    medical_support: bool = False
    water_available: bool = False


class FieldMessageRequest(BaseModel):
    sender_name: str = Field(default="Resident", min_length=1, max_length=96)
    category: str = Field(default="other", max_length=64)
    message: str = Field(min_length=3, max_length=1000)
    segment_id: int | None = None


class FieldMessageStatusRequest(BaseModel):
    status: Literal["open", "in_review", "resolved"]


class FieldMessageResponse(BaseModel):
    id: int
    sender_name: str
    sender_role: str
    category: str
    message: str
    segment_id: int | None
    road_name: str | None
    status: str
    created_at: str
    updated_at: str
