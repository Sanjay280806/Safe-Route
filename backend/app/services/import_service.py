from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import MOCK_DATA_DIR, VELACHERY_DATA_DIR, settings
from app.models import Poi, RoadSegment, Scenario, ShelterDetail
from app.services.geo_service import get_or_create_node, nearest_node
from app.utils.geo_math import line_length_m, normalize_linestring_coordinates, risk_level_for_score


HAZARD_PRIORS = {
    "very_high": (1.0, 1.0),
    "high": (0.8, 0.8),
    "moderate": (0.5, 0.5),
    "low": (0.2, 0.2),
    "unknown": (0.35, 0.35),
}

PLACEHOLDER_FLOOD_TO_RISK = {
    "confirmed_flooded": (0.82, "critical", 0),
    "likely_flooded": (0.62, "high", 18),
    "possible_risk": (0.38, "moderate", 45),
    "safe": (0.12, "low", 120),
    "unknown": (0.25, "moderate", 90),
}


def resolve_data_path(velachery_name: str, mock_name: str) -> Path:
    velachery_path = VELACHERY_DATA_DIR / velachery_name
    mock_path = MOCK_DATA_DIR / mock_name
    if velachery_path.exists():
        return velachery_path
    return mock_path


def import_all(db: Session, *, force: bool = False) -> dict[str, int]:
    roads_path = resolve_data_path("roads.geojson", "roads.geojson")
    pois_path = resolve_data_path("pois.json", "pois.json")
    scenarios_path = resolve_data_path("scenarios.json", "scenarios.json")

    road_count = import_roads(db, roads_path, force=force)
    poi_count = import_pois(db, pois_path, force=force)
    scenario_count = import_scenarios(db, scenarios_path)
    db.commit()
    return {"roads": road_count, "pois": poi_count, "scenarios": scenario_count}


def import_roads(db: Session, path: Path, *, force: bool = False) -> int:
    if not path.exists():
        return 0
    existing = db.query(RoadSegment).count()
    if existing and not force:
        return existing

    payload = json.loads(path.read_text(encoding="utf-8"))
    created = 0
    for feature in payload.get("features", []):
        geometry = feature.get("geometry") or {}
        properties = feature.get("properties") or {}
        sequences = _coordinate_sequences(geometry)
        for coordinates in sequences:
            coords = normalize_linestring_coordinates(coordinates)
            if len(coords) < 2:
                continue
            if coords[0] == coords[-1] and len(coords) == 2:
                continue
            start = get_or_create_node(db, coords[0][0], coords[0][1])
            end = get_or_create_node(db, coords[-1][0], coords[-1][1])
            length_m = float(properties.get("length_m") or line_length_m(coords))
            name = properties.get("name")
            hazard = str(properties.get("hazard_category") or "unknown")
            low_lying, drainage = HAZARD_PRIORS.get(hazard, HAZARD_PRIORS["unknown"])
            if properties.get("low_lying_prior") is not None:
                low_lying = float(properties["low_lying_prior"])
            if properties.get("drainage_proxy") is not None:
                drainage = float(properties["drainage_proxy"])
            flood_status = str(properties.get("flood_status") or "unknown")
            blocked = 1 if properties.get("blocked") else 0
            risk_score, risk_level, predicted = _placeholder_risk(properties, flood_status, blocked)
            is_underpass = _is_underpass(properties, name)
            segment = RoadSegment(
                osm_way_id=str(properties.get("osm_id") or properties.get("osm_way_id") or properties.get("id") or "") or None,
                name=name,
                road_type=str(properties.get("highway") or properties.get("road_type") or "unclassified"),
                from_node_id=start.id,
                to_node_id=end.id,
                length_m=max(length_m, 0.0),
                geometry_json=json.dumps(coords),
                is_underpass=1 if is_underpass else 0,
                low_lying_prior=low_lying,
                proximity_to_water=float(properties.get("proximity_to_water") or 0.5),
                drainage_proxy=drainage,
                hazard_category=hazard,
                historical_flood_count=int(properties.get("historical_flood_count") or 0),
                ml_static_propensity=properties.get("ml_static_propensity"),
                current_risk_score=risk_score,
                current_risk_level=risk_level,
                predicted_time_to_high_risk_min=predicted,
                blocked=blocked,
                flood_status=flood_status,
            )
            db.add(segment)
            created += 1
    db.flush()
    return created


def import_pois(db: Session, path: Path, *, force: bool = False) -> int:
    existing = db.query(Poi).count()
    if existing and not force:
        return existing

    items: list[dict] = []
    if path.exists():
        items = json.loads(path.read_text(encoding="utf-8"))
    elif settings.seed_placeholder_shelters:
        items = _placeholder_pois()

    created = 0
    for item in items:
        lat = float(item["lat"])
        lon = float(item["lon"])
        snapped = nearest_node(db, lat, lon)
        poi = Poi(
            external_id=item.get("external_id"),
            name=item["name"],
            category=item.get("category") or "community_center",
            lat=lat,
            lon=lon,
            address=item.get("address") or "",
            phone=item.get("phone") or "",
            status=item.get("status") or "open",
            nearest_node_id=snapped.id if snapped is not None else item.get("nearest_node_id"),
            source=item.get("source") or "placeholder",
            notes=item.get("notes") or "Placeholder POI. Replace with official data.",
        )
        db.add(poi)
        db.flush()
        if poi.category == "shelter":
            db.add(
                ShelterDetail(
                    poi_id=poi.id,
                    capacity_assumed=int(item.get("capacity_assumed") or 100),
                    occupancy_assumed=int(item.get("occupancy_assumed") or 0),
                    elevation_risk=str(item.get("elevation_risk") or "unknown"),
                    accessible=1 if item.get("accessible") else 0,
                    medical_support=1 if item.get("medical_support") else 0,
                    water_available=1 if item.get("water_available") else 0,
                )
            )
        created += 1
    db.flush()
    return created


def import_scenarios(db: Session, path: Path) -> int:
    if not path.exists():
        return db.query(Scenario).count()
    items = json.loads(path.read_text(encoding="utf-8"))
    upserted = 0
    for item in items:
        name = item["name"]
        scenario = db.query(Scenario).filter(Scenario.name == name).one_or_none()
        if scenario is None:
            scenario = Scenario(name=name)
            db.add(scenario)
        scenario.description = item.get("description")
        scenario.rainfall_mm_24h = float(item.get("rainfall_mm_24h") or 0)
        scenario.rainfall_mm_1h = float(item.get("rainfall_mm_1h") or 0)
        scenario.source = item.get("source") or "manual"
        scenario.is_active = 1 if item.get("is_active") else 0
        upserted += 1
    active_count = db.query(Scenario).filter(Scenario.is_active == 1).count()
    if active_count == 0:
        first = db.query(Scenario).order_by(Scenario.id).first()
        if first is not None:
            first.is_active = 1
    db.flush()
    return upserted


def _coordinate_sequences(geometry: dict) -> list[list]:
    geom_type = geometry.get("type")
    coordinates = geometry.get("coordinates") or []
    if geom_type == "LineString":
        return [coordinates]
    if geom_type == "MultiLineString":
        return coordinates
    return []


def _is_underpass(properties: dict, name: str | None) -> bool:
    if properties.get("underpass") is True or properties.get("is_underpass"):
        return True
    lowered = (name or "").lower()
    return "subway" in lowered or "underpass" in lowered


def _placeholder_risk(properties: dict, flood_status: str, blocked: int) -> tuple[float, str, float]:
    if properties.get("current_risk_score") is not None:
        score = float(properties["current_risk_score"])
        level = str(properties.get("current_risk_level") or risk_level_for_score(score))
        predicted = properties.get("predicted_time_to_high_risk_min")
        return score, level, float(predicted) if predicted is not None else 120.0
    if blocked:
        return 0.95, "critical", 0.0
    score, level, predicted = PLACEHOLDER_FLOOD_TO_RISK.get(flood_status, PLACEHOLDER_FLOOD_TO_RISK["unknown"])
    return score, level, float(predicted)


def _placeholder_pois() -> list[dict]:
    return [
        {
            "external_id": "POI-HOSP-001",
            "name": "Velachery Hospital (Placeholder)",
            "category": "hospital",
            "lat": 12.9820,
            "lon": 80.2150,
            "address": "Hospital Road",
            "status": "open",
            "source": "placeholder",
            "notes": "Replace with real hospital data",
        },
        {
            "external_id": "POI-SHEL-001",
            "name": "Community Shelter (Placeholder)",
            "category": "shelter",
            "lat": 12.9810,
            "lon": 80.2110,
            "address": "Near Main Road",
            "status": "open",
            "source": "placeholder",
            "notes": "Replace with GCC relief centre data",
        },
        {
            "external_id": "POI-POL-001",
            "name": "Police Station (Placeholder)",
            "category": "police_station",
            "lat": 12.9790,
            "lon": 80.2140,
            "address": "Link Road",
            "status": "open",
            "source": "placeholder",
            "notes": "Replace with real police station data",
        },
        {
            "external_id": "POI-FUEL-001",
            "name": "Petrol Bunk (Placeholder)",
            "category": "petrol_bunk",
            "lat": 12.9795,
            "lon": 80.2120,
            "address": "Inner Road",
            "status": "open",
            "source": "placeholder",
            "notes": "Replace with real fuel station data",
        },
    ]
