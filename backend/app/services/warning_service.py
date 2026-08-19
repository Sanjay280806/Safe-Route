from __future__ import annotations

from app.services.types import PathResult, RoadSegment, SegmentRisk


class WarningService:
    def warnings_for_path(
        self,
        path: PathResult,
        segments: dict[int, RoadSegment],
        risks: dict[int, SegmentRisk],
    ) -> list[dict]:
        warnings: list[dict] = []
        eta = 0.0
        for segment_id in path.segment_ids:
            segment = segments[segment_id]
            risk = risks[segment_id]
            if segment.blocked:
                warnings.append(
                    {
                        "warning_type": "blocked_segment",
                        "segment_id": segment.id,
                        "road_name": segment.name,
                        "eta_to_segment_min": round(eta, 1),
                        "predicted_time_to_high_risk_min": 0.0,
                        "message": "This road is confirmed blocked. Rerouting is recommended.",
                    }
                )
            elif (
                risk.predicted_time_to_high_risk_min is not None
                and eta > risk.predicted_time_to_high_risk_min
            ):
                warnings.append(
                    {
                        "warning_type": "predicted_flood_before_arrival",
                        "segment_id": segment.id,
                        "road_name": segment.name,
                        "eta_to_segment_min": round(eta, 1),
                        "predicted_time_to_high_risk_min": round(risk.predicted_time_to_high_risk_min, 1),
                        "message": "This road may become high-risk before you reach it.",
                    }
                )
            eta += segment.length_m / 4.5 / 60.0
        return warnings

