from __future__ import annotations

import heapq
from itertools import count

from app.config import BLOCKED_PENALTY, DEFAULT_SPEED_MPS, SNAP_RADIUS_METERS
from app.repositories.benchmark_repository import BenchmarkRepository
from app.services.explanation_service import ExplanationService
from app.services.graph_service import GraphService
from app.services.risk_service import RiskService
from app.services.time_risk_service import TimeRiskService
from app.services.types import PathResult, Poi, RoadSegment, SegmentRisk
from app.services.warning_service import WarningService


class RouteNotFoundError(Exception):
    pass


class DestinationNotFoundError(Exception):
    pass


class OriginNotSnappableError(Exception):
    pass


class RoutingService:
    def __init__(self, repository: BenchmarkRepository) -> None:
        self.repository = repository
        self.risk_service = RiskService()
        self.time_risk_service = TimeRiskService()
        self.warning_service = WarningService()
        self.explanation_service = ExplanationService()

    def create_route(
        self,
        origin_lat: float,
        origin_lon: float,
        destination: dict,
        route_mode: str = "safe",
        scenario_id: int | None = None,
        include_alternatives: bool = True,
    ) -> dict:
        nodes = self.repository.load_nodes()
        segments = self.repository.load_segments()
        graph = GraphService(nodes, segments)
        scenario = self.repository.load_scenario(scenario_id)
        base_risks = self.risk_service.compute_all(segments, scenario)
        risks = self.time_risk_service.enrich_all(segments, scenario, base_risks)

        origin_node_id = self.repository.snap_node_id(origin_lat, origin_lon, SNAP_RADIUS_METERS)
        if origin_node_id is None:
            raise OriginNotSnappableError("Selected origin is too far from a road.")

        destination_node_id, destination_payload = self._resolve_destination(destination)
        segment_lookup = {segment.id: segment for segment in segments}

        wanted_modes = self._wanted_modes(route_mode, include_alternatives)
        computed: dict[str, PathResult | None] = {}
        for mode in wanted_modes:
            computed[mode] = self._dijkstra(
                graph=graph,
                start_node_id=origin_node_id,
                end_node_id=destination_node_id,
                segments=segment_lookup,
                risks=risks,
                mode=mode,
            )

        if not any(computed.values()):
            raise RouteNotFoundError("No route found for the selected destination.")

        response_routes = []
        all_warnings = []
        for mode in wanted_modes:
            path = computed.get(mode)
            if path is None:
                continue
            warnings = self.warning_service.warnings_for_path(path, segment_lookup, risks)
            all_warnings.extend(warnings)
            response_routes.append(
                {
                    "route_type": path.route_type,
                    "distance_m": round(path.distance_m, 1),
                    "duration_min": round(path.duration_min, 1),
                    "cost_score": round(path.cost_score, 2),
                    "avg_risk_score": round(path.avg_risk_score, 2),
                    "high_risk_segments_count": path.high_risk_segments_count,
                    "blocked_segments_encountered": path.blocked_segments_encountered,
                    "predicted_risk_warnings_count": len(warnings),
                    "geometry": {"type": "LineString", "coordinates": path.geometry},
                }
            )

        safe = computed.get("safe")
        # A shortest-path baseline is calculated only to explain why the one
        # recommendation is safer. It is intentionally not returned to the UI.
        short = self._dijkstra(
            graph=graph,
            start_node_id=origin_node_id,
            end_node_id=destination_node_id,
            segments=segment_lookup,
            risks=risks,
            mode="short",
        ) if safe is not None else None
        return {
            "request_id": self.repository.create_route_request(),
            "destination": destination_payload,
            "routes": response_routes,
            "warnings": self._dedupe_warnings(all_warnings),
            "explanation": self.explanation_service.build(safe, short),
        }

    def _resolve_destination(self, destination: dict) -> tuple[int, dict]:
        if destination.get("poi_id") is not None:
            poi = self.repository.get_poi(int(destination["poi_id"]))
            if poi is None:
                raise DestinationNotFoundError("Destination POI was not found.")
            node_id = poi.nearest_node_id or self.repository.snap_node_id(poi.lat, poi.lon, SNAP_RADIUS_METERS)
            if node_id is None:
                raise DestinationNotFoundError("Destination POI is too far from a road.")
            return int(node_id), self._poi_payload(poi)

        lat = destination.get("lat")
        lon = destination.get("lon")
        if lat is None or lon is None:
            raise DestinationNotFoundError("Destination must include poi_id or lat/lon.")
        node_id = self.repository.snap_node_id(float(lat), float(lon), SNAP_RADIUS_METERS)
        if node_id is None:
            raise DestinationNotFoundError("Destination is too far from a road.")
        return node_id, {"type": "custom", "lat": float(lat), "lon": float(lon)}

    def _poi_payload(self, poi: Poi) -> dict:
        return {
            "type": "poi",
            "poi_id": poi.id,
            "name": poi.name,
            "category": poi.category,
        }

    def _wanted_modes(self, route_mode: str, include_alternatives: bool) -> list[str]:
        # The dashboard presents one flood-aware recommendation.  Keep accepting
        # legacy request parameters so existing clients remain compatible, but
        # never return a less-safe alternative as a competing recommendation.
        return ["safe"]

    def _dijkstra(
        self,
        graph: GraphService,
        start_node_id: int,
        end_node_id: int,
        segments: dict[int, RoadSegment],
        risks: dict[int, SegmentRisk],
        mode: str,
    ) -> PathResult | None:
        tie = count()
        queue: list[tuple[float, int, int, float, list[int], list[int]]] = [
            (0.0, next(tie), start_node_id, 0.0, [], [start_node_id])
        ]
        best_cost: dict[int, float] = {start_node_id: 0.0}

        while queue:
            cost, _, node_id, eta_min, path_segments, path_nodes = heapq.heappop(queue)
            if node_id == end_node_id:
                return self._path_result(mode, path_segments, path_nodes, graph, segments, risks, cost)
            if cost > best_cost.get(node_id, float("inf")):
                continue

            for neighbor_id, segment_id in graph.get_neighbors(node_id):
                segment = segments[segment_id]
                edge_time = segment.length_m / DEFAULT_SPEED_MPS / 60.0
                edge_cost = self._edge_cost(segment, risks[segment_id], eta_min, mode)
                next_cost = cost + edge_cost
                if next_cost < best_cost.get(neighbor_id, float("inf")):
                    best_cost[neighbor_id] = next_cost
                    heapq.heappush(
                        queue,
                        (
                            next_cost,
                            next(tie),
                            neighbor_id,
                            eta_min + edge_time,
                            [*path_segments, segment_id],
                            [*path_nodes, neighbor_id],
                        ),
                    )
        return None

    def _edge_cost(self, segment: RoadSegment, risk: SegmentRisk, eta_min: float, mode: str) -> float:
        travel_time_min = segment.length_m / DEFAULT_SPEED_MPS / 60.0
        blocked_penalty = BLOCKED_PENALTY if segment.blocked else 0.0
        if mode == "short":
            return travel_time_min + blocked_penalty

        current_risk_penalty = risk.risk_score * risk.risk_score * 0.015 * segment.length_m
        predicted_penalty = 0.0
        if (
            risk.predicted_time_to_high_risk_min is not None
            and eta_min > risk.predicted_time_to_high_risk_min
        ):
            predicted_penalty = 20.0
        return travel_time_min + current_risk_penalty + predicted_penalty + blocked_penalty

    def _path_result(
        self,
        mode: str,
        segment_ids: list[int],
        node_ids: list[int],
        graph: GraphService,
        segments: dict[int, RoadSegment],
        risks: dict[int, SegmentRisk],
        cost_score: float,
    ) -> PathResult:
        distance_m = sum(segments[segment_id].length_m for segment_id in segment_ids)
        duration_min = distance_m / DEFAULT_SPEED_MPS / 60.0
        avg_risk = (
            sum(risks[segment_id].risk_score for segment_id in segment_ids) / len(segment_ids)
            if segment_ids
            else 0.0
        )
        high_count = sum(1 for segment_id in segment_ids if risks[segment_id].risk_level in {"high", "critical"})
        blocked_count = sum(1 for segment_id in segment_ids if segments[segment_id].blocked)
        geometry = self._path_geometry(segment_ids, node_ids, graph)
        return PathResult(
            route_type=mode,
            segment_ids=segment_ids,
            node_ids=node_ids,
            distance_m=distance_m,
            duration_min=duration_min,
            cost_score=cost_score,
            avg_risk_score=avg_risk,
            high_risk_segments_count=high_count,
            blocked_segments_encountered=blocked_count,
            geometry=geometry,
        )

    def _path_geometry(self, segment_ids: list[int], node_ids: list[int], graph: GraphService) -> list[list[float]]:
        coordinates: list[list[float]] = []
        for index, segment_id in enumerate(segment_ids):
            line = graph.line_for_segment(segment_id, node_ids[index], node_ids[index + 1])
            if coordinates and line and coordinates[-1] == line[0]:
                coordinates.extend(line[1:])
            else:
                coordinates.extend(line)
        return coordinates

    def _dedupe_warnings(self, warnings: list[dict]) -> list[dict]:
        seen = set()
        deduped = []
        for warning in warnings:
            key = (warning["warning_type"], warning["segment_id"])
            if key not in seen:
                seen.add(key)
                deduped.append(warning)
        return deduped
