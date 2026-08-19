from __future__ import annotations

from collections import defaultdict

from app.services.types import Node, RoadSegment


class GraphService:
    def __init__(self, nodes: list[Node], segments: list[RoadSegment]) -> None:
        self.nodes = {node.id: node for node in nodes}
        self.segments = {segment.id: segment for segment in segments}
        self.adjacency: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for segment in segments:
            self.adjacency[segment.from_node_id].append((segment.to_node_id, segment.id))
            self.adjacency[segment.to_node_id].append((segment.from_node_id, segment.id))

    def get_neighbors(self, node_id: int) -> list[tuple[int, int]]:
        return self.adjacency.get(node_id, [])

    def get_segment(self, segment_id: int) -> RoadSegment:
        return self.segments[segment_id]

    def line_for_segment(self, segment_id: int, from_node_id: int, to_node_id: int) -> list[list[float]]:
        segment = self.get_segment(segment_id)
        if segment.from_node_id == from_node_id and segment.to_node_id == to_node_id:
            return segment.geometry
        return list(reversed(segment.geometry))

