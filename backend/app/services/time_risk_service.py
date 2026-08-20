from __future__ import annotations

from app.ai.predict import predict_all
from app.services.types import RoadSegment, Scenario, SegmentRisk
from app.utils.geo_math import clamp


class TimeRiskService:
    def predict_time_to_high_risk(
        self,
        segment: RoadSegment,
        scenario: Scenario,
        risk: SegmentRisk,
        static_propensity: float | None = None,
    ) -> float:
        if segment.blocked or risk.risk_score >= 0.75:
            return 0.0

        rain_factor = clamp(scenario.rainfall_mm_1h / 50.0, 0.1, 2.0)
        propensity = static_propensity
        if propensity is None:
            propensity = predict_all([segment]).get(segment.id, segment.drainage_proxy)
        predicted_time = ((1.0 - clamp(float(propensity), 0.0, 1.0)) * 120.0) / rain_factor
        if segment.is_underpass:
            predicted_time *= 0.6
        return clamp(predicted_time, 5.0, 180.0)

    def enrich_all(
        self,
        segments: list[RoadSegment],
        scenario: Scenario,
        risks: dict[int, SegmentRisk],
    ) -> dict[int, SegmentRisk]:
        propensities = predict_all(segments)
        enriched: dict[int, SegmentRisk] = {}
        for segment in segments:
            risk = risks[segment.id]
            enriched[segment.id] = SegmentRisk(
                segment_id=risk.segment_id,
                risk_score=risk.risk_score,
                risk_level=risk.risk_level,
                predicted_time_to_high_risk_min=self.predict_time_to_high_risk(
                    segment, scenario, risk, propensities.get(segment.id)
                ),
            )
        return enriched
