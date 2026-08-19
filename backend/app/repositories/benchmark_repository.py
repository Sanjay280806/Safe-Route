from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TYPE_CHECKING

try:
    from sqlalchemy import inspect, text
except ImportError:
    inspect = None
    text = None

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
else:
    Session = Any

from app.config import MOCK_DATA_DIR
from app.services.types import Node, Poi, RoadSegment, Scenario
from app.utils.geo_math import haversine_m, normalize_linestring_coordinates


class BenchmarkRepository:
    """Reads existing DB tables by convention, with placeholder mock fallback."""

    def __init__(self, db: Session | None = None) -> None:
        self.db = db

    def load_nodes(self) -> list[Node]:
        if self._has_table("nodes"):
            rows = self.db.execute(text("SELECT id, lat, lon FROM nodes")).mappings().all()
            return [Node(id=int(r["id"]), lat=float(r["lat"]), lon=float(r["lon"])) for r in rows]
        segments = self.load_segments()
        seen: dict[str, Node] = {}
        next_id = 1
        for segment in segments:
            for lon, lat in (segment.geometry[0], segment.geometry[-1]):
                key = f"{lat:.7f},{lon:.7f}"
                if key not in seen:
                    seen[key] = Node(id=next_id, lat=lat, lon=lon)
                    next_id += 1
        return list(seen.values())

    def load_segments(self) -> list[RoadSegment]:
        if self._has_table("road_segments"):
            rows = self.db.execute(text("SELECT * FROM road_segments")).mappings().all()
            return [self._segment_from_row(dict(row)) for row in rows]
        return self._load_mock_segments()

    def load_scenario(self, scenario_id: int | None = None) -> Scenario:
        scenarios = self.load_scenarios()
        if scenario_id is not None:
            for scenario in scenarios:
                if scenario.id == scenario_id:
                    return scenario
        for scenario in scenarios:
            if scenario.is_active:
                return scenario
        return scenarios[0]

    def load_scenarios(self) -> list[Scenario]:
        if self._has_table("scenarios"):
            rows = self.db.execute(text("SELECT * FROM scenarios")).mappings().all()
            scenarios = []
            for r in rows:
                scenarios.append(
                    Scenario(
                        id=int(r["id"]),
                        name=str(r.get("name") or "Scenario"),
                        rainfall_mm_24h=float(r.get("rainfall_mm_24h") or 0),
                        rainfall_mm_1h=float(r.get("rainfall_mm_1h") or 0),
                        is_active=bool(r.get("is_active", False)),
                    )
                )
            if scenarios:
                return scenarios
        payload = self._read_json(MOCK_DATA_DIR / "scenarios.json")
        return [
            Scenario(
                id=int(item["id"]),
                name=str(item["name"]),
                rainfall_mm_24h=float(item["rainfall_mm_24h"]),
                rainfall_mm_1h=float(item["rainfall_mm_1h"]),
                is_active=bool(item.get("is_active", False)),
            )
            for item in payload
        ]

    def get_poi(self, poi_id: int) -> Poi | None:
        if self._has_table("pois"):
            row = self.db.execute(text("SELECT * FROM pois WHERE id = :id"), {"id": poi_id}).mappings().first()
            if row:
                return self._poi_from_row(dict(row))
        for poi in self._load_mock_pois():
            if poi.id == poi_id:
                return poi
        return None

    def create_route_request(self) -> int:
        if self._has_table("route_requests"):
            try:
                result = self.db.execute(text("INSERT INTO route_requests DEFAULT VALUES"))
                self.db.commit()
                return int(result.lastrowid or 0)
            except Exception:
                self.db.rollback()
        return 1

    def snap_node_id(self, lat: float, lon: float, max_distance_m: float) -> int | None:
        nearest_id = None
        nearest_distance = max_distance_m
        for node in self.load_nodes():
            distance = haversine_m(lat, lon, node.lat, node.lon)
            if distance <= nearest_distance:
                nearest_id = node.id
                nearest_distance = distance
        return nearest_id

    def _has_table(self, table_name: str) -> bool:
        if self.db is None or inspect is None:
            return False
        try:
            return inspect(self.db.bind).has_table(table_name)
        except Exception:
            return False

    def _segment_from_row(self, row: dict[str, Any]) -> RoadSegment:
        raw_geometry = row.get("geometry_json") or row.get("geometry") or "[]"
        if isinstance(raw_geometry, str):
            parsed = json.loads(raw_geometry)
            raw_geometry = parsed.get("coordinates", parsed) if isinstance(parsed, dict) else parsed
        return RoadSegment(
            id=int(row["id"]),
            from_node_id=int(row["from_node_id"]),
            to_node_id=int(row["to_node_id"]),
            length_m=float(row.get("length_m") or 0),
            geometry=normalize_linestring_coordinates(raw_geometry),
            name=str(row.get("name") or "Unnamed road"),
            road_type=str(row.get("road_type") or "unclassified"),
            is_underpass=bool(row.get("is_underpass", False)),
            low_lying_prior=float(row.get("low_lying_prior") or 0.35),
            proximity_to_water=float(row.get("proximity_to_water") or 0.5),
            drainage_proxy=float(row.get("drainage_proxy") or 0.5),
            historical_flood_count=int(row.get("historical_flood_count") or 0),
            ml_static_propensity=row.get("ml_static_propensity"),
            blocked=bool(row.get("blocked", False)),
            flood_status=str(row.get("flood_status") or "safe"),
        )

    def _poi_from_row(self, row: dict[str, Any]) -> Poi:
        return Poi(
            id=int(row["id"]),
            name=str(row["name"]),
            category=str(row.get("category") or row.get("type") or "poi"),
            lat=float(row["lat"]),
            lon=float(row["lon"]),
            nearest_node_id=row.get("nearest_node_id"),
            status=str(row.get("status") or "open"),
        )

    def _load_mock_segments(self) -> list[RoadSegment]:
        payload = self._read_json(MOCK_DATA_DIR / "roads.geojson")
        features = payload["features"]
        return [
            RoadSegment(
                id=int(feature["properties"]["segment_id"]),
                from_node_id=int(feature["properties"]["from_node_id"]),
                to_node_id=int(feature["properties"]["to_node_id"]),
                length_m=float(feature["properties"]["length_m"]),
                geometry=normalize_linestring_coordinates(feature["geometry"]["coordinates"]),
                name=str(feature["properties"]["name"]),
                road_type=str(feature["properties"].get("road_type", "residential")),
                is_underpass=bool(feature["properties"].get("is_underpass", False)),
                low_lying_prior=float(feature["properties"].get("low_lying_prior", 0.35)),
                proximity_to_water=float(feature["properties"].get("proximity_to_water", 0.5)),
                drainage_proxy=float(feature["properties"].get("drainage_proxy", 0.5)),
                historical_flood_count=int(feature["properties"].get("historical_flood_count", 0)),
                ml_static_propensity=feature["properties"].get("ml_static_propensity"),
                blocked=bool(feature["properties"].get("blocked", False)),
                flood_status=str(feature["properties"].get("flood_status", "safe")),
            )
            for feature in features
        ]

    def _load_mock_pois(self) -> list[Poi]:
        return [self._poi_from_row(item) for item in self._read_json(MOCK_DATA_DIR / "pois.json")]

    def _read_json(self, path: Path) -> Any:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
