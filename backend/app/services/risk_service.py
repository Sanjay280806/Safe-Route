from __future__ import annotations

from app.ai.predict import predict_all
from app.services.types import RoadSegment, Scenario, SegmentRisk
from app.utils.geo_math import clamp, risk_level_for_score


class RiskService:
    def compute_risk(
        self,
        segment: RoadSegment,
        scenario: Scenario,
        static_propensity: float | None = None,
    ) -> SegmentRisk:
        combined_rain = min(
            1.0,
            (0.7 * min(1.0, scenario.rainfall_mm_24h / 150.0))
            + (0.3 * min(1.0, scenario.rainfall_mm_1h / 30.0)),
        )
        propensity = (
            static_propensity
            if static_propensity is not None
            else predict_all([segment]).get(segment.id)
        )
        if propensity is None:
            propensity = (
                segment.ml_static_propensity
                if segment.ml_static_propensity is not None
                else segment.drainage_proxy
            )
        blocked_factor = 1.0 if segment.blocked else 0.0
        underpass_factor = 1.0 if segment.is_underpass else 0.0
        score = (
            0.45 * combined_rain
            + 0.30 * clamp(float(propensity), 0.0, 1.0)
            + 0.10 * underpass_factor
            + 0.10 * blocked_factor
            + 0.05 * clamp(segment.low_lying_prior, 0.0, 1.0)
        )
        if segment.blocked:
            score = max(score, 0.95)
        score = clamp(score, 0.0, 1.0)
        return SegmentRisk(
            segment_id=segment.id,
            risk_score=score,
            risk_level=risk_level_for_score(score),
            predicted_time_to_high_risk_min=None,
        )

    def compute_all(self, segments: list[RoadSegment], scenario: Scenario) -> dict[int, SegmentRisk]:
        propensities = predict_all(segments)
        return {
            segment.id: self.compute_risk(segment, scenario, propensities.get(segment.id))
            for segment in segments
        }
