from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.predict import model_is_loaded, model_meta, predict_all
from app.models import RiskSnapshot, RoadSegment, Scenario
from app.repositories.benchmark_repository import BenchmarkRepository
from app.services.risk_service import RiskService
from app.services.time_risk_service import TimeRiskService
from app.utils.errors import APIError


DOCUMENTED_FLOOD_POCKETS = [
    "AGS Colony",
    "Baby Nagar",
    "Dhandeeswaran Nagar",
    "Venkateshwara Nagar",
    "EB Colony",
    "Ayothi Colony",
    "Vijayanagar",
    "Ramnagar",
    "Murugan Nagar",
    "Kuberan Nagar",
]


def recompute_active_scenario_risk(db: Session, scenario_id: int | None = None) -> dict:
    repository = BenchmarkRepository(db)
    scenario = repository.load_scenario(scenario_id)
    if scenario is None:
        raise APIError(422, "NO_ACTIVE_SCENARIO", "No active scenario is available.")

    segments = repository.load_segments()
    base_risks = RiskService().compute_all(segments, scenario)
    risks = TimeRiskService().enrich_all(segments, scenario, base_risks)
    propensities = predict_all(segments)
    model_loaded = model_is_loaded()
    source = "isolation_forest" if model_loaded else "heuristic_fallback"
    now = datetime.now(timezone.utc)

    orm_segments = {row.id: row for row in db.query(RoadSegment).all()}
    updated = 0
    for segment in segments:
        risk = risks[segment.id]
        propensity = propensities.get(segment.id)
        orm = orm_segments.get(segment.id)
        if orm is not None:
            orm.current_risk_score = risk.risk_score
            orm.current_risk_level = risk.risk_level
            orm.predicted_time_to_high_risk_min = risk.predicted_time_to_high_risk_min
            if propensity is not None:
                orm.ml_static_propensity = float(propensity)
            orm.updated_at = now

        snapshot = (
            db.query(RiskSnapshot)
            .filter(RiskSnapshot.scenario_id == scenario.id, RiskSnapshot.segment_id == segment.id)
            .one_or_none()
        )
        factors = json.dumps(
            {
                "source": source,
                "static_propensity": None if propensity is None else round(float(propensity), 4),
                "risk_score": round(risk.risk_score, 4),
                "risk_level": risk.risk_level,
            }
        )
        if snapshot is None:
            db.add(
                RiskSnapshot(
                    scenario_id=scenario.id,
                    segment_id=segment.id,
                    risk_score=risk.risk_score,
                    risk_level=risk.risk_level,
                    factors_json=factors,
                    computed_at=now,
                )
            )
        else:
            snapshot.risk_score = risk.risk_score
            snapshot.risk_level = risk.risk_level
            snapshot.factors_json = factors
            snapshot.computed_at = now
        updated += 1

    db.commit()
    return {"scenario_id": scenario.id, "segments_updated": updated, "model_loaded": model_loaded}


def validation_summary(db: Session) -> dict:
    repository = BenchmarkRepository(db)
    scenario = repository.load_scenario()
    segments = repository.load_segments()
    risks = TimeRiskService().enrich_all(segments, scenario, RiskService().compute_all(segments, scenario))
    distribution = {"low": 0, "moderate": 0, "high": 0, "critical": 0}
    ranked = []
    for segment in segments:
        risk = risks[segment.id]
        if risk.risk_level in distribution:
            distribution[risk.risk_level] += 1
        ranked.append(
            {
                "segment_id": segment.id,
                "name": segment.name,
                "risk_score": round(risk.risk_score, 2),
                "risk_level": risk.risk_level,
            }
        )
    ranked.sort(key=lambda item: item["risk_score"], reverse=True)
    meta = model_meta()
    loaded = model_is_loaded()
    return {
        "model_loaded": loaded,
        "model_type": "IsolationForest" if loaded else str(meta.get("model_type") or "heuristic_fallback"),
        "segment_count": len(segments),
        "risk_distribution": distribution,
        "top_high_risk_segments": ranked[:5],
        "documented_flood_pockets": DOCUMENTED_FLOOD_POCKETS,
    }
