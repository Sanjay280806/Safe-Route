from __future__ import annotations

from app.services.types import PathResult


class ExplanationService:
    def build(self, safe: PathResult | None, short: PathResult | None) -> dict:
        if safe is None and short is None:
            return {
                "safe_route_adds_min": 0.0,
                "high_risk_segments_avoided": 0,
                "blocked_segments_avoided": 0,
                "summary": "No route could be computed for the selected destination.",
            }
        if safe is None:
            return {
                "safe_route_adds_min": 0.0,
                "high_risk_segments_avoided": 0,
                "blocked_segments_avoided": 0,
                "summary": "Only the shortest route was available for this request.",
            }
        if short is None:
            return {
                "safe_route_adds_min": 0.0,
                "high_risk_segments_avoided": safe.high_risk_segments_count,
                "blocked_segments_avoided": safe.blocked_segments_encountered,
                "summary": "Safest route computed using flood risk and blocked-road penalties.",
            }

        adds = max(0.0, safe.duration_min - short.duration_min)
        high_avoided = max(0, short.high_risk_segments_count - safe.high_risk_segments_count)
        blocked_avoided = max(0, short.blocked_segments_encountered - safe.blocked_segments_encountered)
        if high_avoided or blocked_avoided:
            summary = "Safe route avoids flood-prone or blocked road segments while keeping travel time practical."
        elif safe.avg_risk_score < short.avg_risk_score:
            summary = "Safe route lowers overall flood exposure compared with the shortest route."
        else:
            summary = "Safe and short routes have similar flood exposure for this scenario."
        return {
            "safe_route_adds_min": round(adds, 1),
            "high_risk_segments_avoided": high_avoided,
            "blocked_segments_avoided": blocked_avoided,
            "summary": summary,
        }

