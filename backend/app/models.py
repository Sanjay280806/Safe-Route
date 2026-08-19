from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="public")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    lon_lat_key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)


class RoadSegment(Base):
    __tablename__ = "road_segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    osm_way_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    road_type: Mapped[str] = mapped_column(String(64), nullable=False, default="unclassified")
    from_node_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"), index=True, nullable=False)
    to_node_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"), index=True, nullable=False)
    length_m: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    geometry_json: Mapped[str] = mapped_column(Text, nullable=False)
    is_underpass: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    low_lying_prior: Mapped[float] = mapped_column(Float, nullable=False, default=0.35)
    proximity_to_water: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    drainage_proxy: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    hazard_category: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    historical_flood_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ml_static_propensity: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    current_risk_level: Mapped[str] = mapped_column(String(32), nullable=False, default="low", index=True)
    predicted_time_to_high_risk_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    blocked: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    flood_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    active_report_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    from_node: Mapped[Node] = relationship(foreign_keys=[from_node_id])
    to_node: Mapped[Node] = relationship(foreign_keys=[to_node_id])


class Poi(Base):
    __tablename__ = "pois"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    nearest_node_id: Mapped[int | None] = mapped_column(ForeignKey("nodes.id"), nullable=True)
    source: Mapped[str] = mapped_column(String(120), nullable=False, default="placeholder")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    nearest_node: Mapped[Node | None] = relationship()
    shelter_details: Mapped["ShelterDetail | None"] = relationship(back_populates="poi", uselist=False)


class ShelterDetail(Base):
    __tablename__ = "shelter_details"

    poi_id: Mapped[int] = mapped_column(ForeignKey("pois.id"), primary_key=True)
    capacity_assumed: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    occupancy_assumed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    elevation_risk: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    accessible: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    medical_support: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    water_available: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    poi: Mapped[Poi] = relationship(back_populates="shelter_details")


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    rainfall_mm_24h: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rainfall_mm_1h: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source: Mapped[str] = mapped_column(String(120), nullable=False, default="manual")
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class BlockedReport(Base):
    __tablename__ = "blocked_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("road_segments.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="field_official")
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)
    verification_status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    credibility_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    flood_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    segment: Mapped[RoadSegment] = relationship()
    user: Mapped[User] = relationship()


class RouteRequest(Base):
    __tablename__ = "route_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scenario_id: Mapped[int | None] = mapped_column(ForeignKey("scenarios.id"), nullable=True)
    origin_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    origin_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    origin_node_id: Mapped[int | None] = mapped_column(ForeignKey("nodes.id"), nullable=True)
    destination_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    destination_poi_id: Mapped[int | None] = mapped_column(ForeignKey("pois.id"), nullable=True)
    destination_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    destination_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    destination_node_id: Mapped[int | None] = mapped_column(ForeignKey("nodes.id"), nullable=True)
    route_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="safe")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class RouteResult(Base):
    __tablename__ = "route_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("route_requests.id"), index=True, nullable=False)
    route_type: Mapped[str] = mapped_column(String(32), nullable=False)
    poi_id: Mapped[int | None] = mapped_column(ForeignKey("pois.id"), nullable=True)
    node_sequence_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    edge_sequence_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    geometry_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    distance_m: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    duration_min: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cost_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    high_risk_segments_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    blocked_segments_encountered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    predicted_risk_warnings_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class RouteWarning(Base):
    __tablename__ = "route_warnings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_result_id: Mapped[int] = mapped_column(ForeignKey("route_results.id"), nullable=False)
    segment_id: Mapped[int | None] = mapped_column(ForeignKey("road_segments.id"), nullable=True)
    warning_type: Mapped[str] = mapped_column(String(64), nullable=False)
    eta_to_segment_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_time_to_high_risk_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class RiskSnapshot(Base):
    __tablename__ = "risk_snapshots"
    __table_args__ = (UniqueConstraint("scenario_id", "segment_id", name="uq_risk_snapshots_scenario_segment"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("scenarios.id"), nullable=False)
    segment_id: Mapped[int] = mapped_column(ForeignKey("road_segments.id"), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False)
    factors_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
