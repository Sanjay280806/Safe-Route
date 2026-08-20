from __future__ import annotations

import json
from datetime import datetime, timezone

try:
    from sqlalchemy import inspect, text
except ImportError:
    inspect = None
    text = None

from app.ai.features import FEATURE_NAMES, segment_features
from app.config import MODEL_DIR, MODEL_META_PATH, MODEL_PATH
from app.database import SessionLocal
from app.repositories.benchmark_repository import BenchmarkRepository
from app.utils.geo_math import clamp


def train() -> dict:
    try:
        from joblib import dump
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise RuntimeError("Install scikit-learn and joblib to train the risk model.") from exc

    db = SessionLocal()
    try:
        repository = BenchmarkRepository(db)
        segments = repository.load_segments()
    finally:
        db.close()

    if len(segments) < 30:
        meta = {
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "segment_count": len(segments),
            "model_type": "not_trained",
            "reason": "fewer_than_30_segments",
            "top_propensity_segments": [],
        }
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        MODEL_META_PATH.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return meta

    x = [segment_features(segment) for segment in segments]
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)
    model = IsolationForest(n_estimators=200, contamination=0.15, random_state=42)
    model.fit(x_scaled)

    scores = model.score_samples(x_scaled)
    min_score = min(scores)
    max_score = max(scores)
    span = max(max_score - min_score, 1e-9)
    propensities = [clamp(1.0 - ((score - min_score) / span), 0.0, 1.0) for score in scores]

    artifact = {
        "model": model,
        "scaler": scaler,
        "feature_names": FEATURE_NAMES,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "segment_count": len(segments),
        "score_min": float(min_score),
        "score_max": float(max_score),
    }
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    dump(artifact, MODEL_PATH)
    try:
        from app.ai.predict import clear_model_cache

        clear_model_cache()
    except Exception:
        pass

    top = sorted(
        [
            {
                "segment_id": segment.id,
                "road_name": segment.name,
                "ml_static_propensity": round(propensity, 3),
            }
            for segment, propensity in zip(segments, propensities)
        ],
        key=lambda item: item["ml_static_propensity"],
        reverse=True,
    )[:10]
    meta = {
        "trained_at": artifact["trained_at"],
        "segment_count": len(segments),
        "model_type": "IsolationForest",
        "top_propensity_segments": top,
    }
    MODEL_META_PATH.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    _update_segment_propensities(segments, propensities)
    return meta


def _update_segment_propensities(segments, propensities: list[float]) -> int:
    if inspect is None or text is None or SessionLocal is None:
        return 0
    db = SessionLocal()
    try:
        inspector = inspect(db.bind)
        if not inspector.has_table("road_segments"):
            return 0
        columns = {column["name"] for column in inspector.get_columns("road_segments")}
        if "ml_static_propensity" not in columns:
            return 0

        updated = 0
        for segment, propensity in zip(segments, propensities):
            db.execute(
                text(
                    "UPDATE road_segments "
                    "SET ml_static_propensity = :propensity "
                    "WHERE id = :segment_id"
                ),
                {"propensity": float(propensity), "segment_id": int(segment.id)},
            )
            updated += 1
        db.commit()
        return updated
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    result = train()
    print(json.dumps(result, indent=2))
