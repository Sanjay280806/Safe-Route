from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models import RiskSnapshot, RoadSegment, Scenario
from app.services.risk_service import RiskService
from app.services.time_risk_service import TimeRiskService
from app.utils.errors import APIError


MODEL_TYPE = "Local rainfall and flood-risk predictor"


def recompute_risk(db: Session, scenario_id: int | None = None) -> dict[str, int | bool]:
    scenario_query = db.query(Scenario)
    scenario = (
        scenario_query.filter(Scenario.id == scenario_id).one_or_none()
        if scenario_id is not None
        else scenario_query.filter(Scenario.is_active == 1).first()
    )
    if scenario is None:
        raise APIError(404, "SCENARIO_NOT_FOUND", "No matching rainfall scenario is available.")

    segments = db.query(RoadSegment).order_by(RoadSegment.id).all()
    risk_by_segment = RiskService().compute_all(segments, scenario)
    enriched = TimeRiskService().enrich_all(segments, scenario, risk_by_segment)

    for segment in segments:
        risk = enriched[segment.id]
        segment.current_risk_score = round(risk.risk_score, 3)
        segment.current_risk_level = risk.risk_level
        segment.predicted_time_to_high_risk_min = risk.predicted_time_to_high_risk_min

        snapshot = (
            db.query(RiskSnapshot)
            .filter(RiskSnapshot.scenario_id == scenario.id, RiskSnapshot.segment_id == segment.id)
            .one_or_none()
        )
        factors = {
            "predictor": "local_benchmark",
            "rainfall_mm_24h": scenario.rainfall_mm_24h,
            "rainfall_mm_1h": scenario.rainfall_mm_1h,
            "blocked": bool(segment.blocked),
        }
        if snapshot is None:
            snapshot = RiskSnapshot(scenario_id=scenario.id, segment_id=segment.id)
            db.add(snapshot)
        snapshot.risk_score = risk.risk_score
        snapshot.risk_level = risk.risk_level
        snapshot.factors_json = json.dumps(factors)

    db.commit()
    return {"scenario_id": scenario.id, "segments_updated": len(segments), "model_loaded": True}


def validation_summary(db: Session) -> dict:
    segments = db.query(RoadSegment).order_by(RoadSegment.current_risk_score.desc(), RoadSegment.id).all()
    distribution = {"low": 0, "moderate": 0, "high": 0, "critical": 0}
    for segment in segments:
        distribution[segment.current_risk_level] = distribution.get(segment.current_risk_level, 0) + 1

    high_risk = [
        {
            "segment_id": segment.id,
            "name": segment.name or f"Road segment {segment.id}",
            "risk_score": round(segment.current_risk_score, 3),
            "risk_level": segment.current_risk_level,
        }
        for segment in segments[:5]
    ]
    flagged = [
        f"{segment.name or f'Road segment {segment.id}'} — seeded or field-reported local risk."
        for segment in segments
        if segment.blocked or segment.current_risk_score >= 0.5
    ]
    return {
        "model_loaded": True,
        "model_type": MODEL_TYPE,
        "segment_count": len(segments),
        "risk_distribution": distribution,
        "top_high_risk_segments": high_risk,
        "documented_flood_pockets": flagged,
    }
