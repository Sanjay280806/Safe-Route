from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BlockedReport, Poi, RoadSegment, Scenario
from app.utils.errors import APIError
from app.utils.geo_math import normalize_linestring_coordinates, segment_midpoint


router = APIRouter(tags=["map"])


@router.get("/map/geojson")
def map_geojson(
    db: Session = Depends(get_db),
    scenario_id: int | None = Query(default=None),
    include: str = Query(default="roads,pois,reports"),
) -> dict:
    requested = {part.strip() for part in include.split(",") if part.strip()}
    allowed = {"roads", "pois", "reports"}
    unknown = requested - allowed
    if unknown:
        raise APIError(422, "VALIDATION_ERROR", "Invalid include value.", {"unknown": sorted(unknown)})

    if scenario_id is not None:
        scenario = db.query(Scenario).filter(Scenario.id == scenario_id).one_or_none()
        if scenario is None:
            raise APIError(404, "SCENARIO_NOT_FOUND", "Scenario was not found.")
    else:
        scenario = db.query(Scenario).filter(Scenario.is_active == 1).first()
        if scenario is None:
            raise APIError(422, "NO_ACTIVE_SCENARIO", "No active scenario is available.")

    features: list[dict] = []
    if "roads" in requested:
        features.extend(_road_features(db))
    if "pois" in requested:
        features.extend(_poi_features(db))
    if "reports" in requested:
        features.extend(_report_features(db))
    return {"type": "FeatureCollection", "features": features}


def _road_features(db: Session) -> list[dict]:
    features = []
    for segment in db.query(RoadSegment).order_by(RoadSegment.id).all():
        coordinates = normalize_linestring_coordinates(json.loads(segment.geometry_json))
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coordinates},
                "properties": {
                    "layer_type": "road",
                    "segment_id": segment.id,
                    "name": segment.name,
                    "road_type": segment.road_type,
                    "current_risk_score": segment.current_risk_score,
                    "current_risk_level": segment.current_risk_level,
                    "predicted_time_to_high_risk_min": segment.predicted_time_to_high_risk_min,
                    "blocked": bool(segment.blocked),
                    "flood_status": segment.flood_status,
                },
            }
        )
    return features


def _poi_features(db: Session) -> list[dict]:
    features = []
    for poi in db.query(Poi).order_by(Poi.id).all():
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [poi.lon, poi.lat]},
                "properties": {
                    "layer_type": "poi",
                    "poi_id": poi.id,
                    "name": poi.name,
                    "category": poi.category,
                    "status": poi.status,
                },
            }
        )
    return features


def _report_features(db: Session) -> list[dict]:
    features = []
    reports = db.query(BlockedReport).filter(BlockedReport.status == "active").all()
    for report in reports:
        segment = db.query(RoadSegment).filter(RoadSegment.id == report.segment_id).one_or_none()
        if segment is None:
            continue
        coordinates = normalize_linestring_coordinates(json.loads(segment.geometry_json))
        lat, lon = segment_midpoint(coordinates)
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "layer_type": "report",
                    "report_id": report.id,
                    "segment_id": report.segment_id,
                    "verification_status": report.verification_status,
                    "source": report.source,
                    "note": report.note,
                },
            }
        )
    return features
