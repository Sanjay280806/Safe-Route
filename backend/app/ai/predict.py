from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path

from app.ai.features import FEATURE_NAMES, segment_features
from app.config import MODEL_META_PATH, MODEL_PATH, settings
from app.utils.geo_math import clamp

logger = logging.getLogger(__name__)


def _model_file() -> Path:
    return Path(settings.model_path or MODEL_PATH)


def clear_model_cache() -> None:
    load_artifact.cache_clear()


@lru_cache(maxsize=1)
def load_artifact() -> dict | None:
    path = _model_file()
    if not path.exists():
        return None
    try:
        from joblib import load

        artifact = load(path)
    except Exception:
        logger.exception("Failed to load flood risk model from %s", path)
        return None
    if not isinstance(artifact, dict) or "model" not in artifact or "scaler" not in artifact:
        logger.error("Flood risk model artifact is missing required keys.")
        return None
    return artifact


def model_is_loaded() -> bool:
    return load_artifact() is not None


def model_meta() -> dict:
    if MODEL_META_PATH.exists():
        try:
            payload = json.loads(MODEL_META_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except Exception:
            logger.exception("Failed to read model metadata")
    artifact = load_artifact()
    if artifact is None:
        return {"model_type": "heuristic_fallback", "segment_count": 0}
    return {
        "model_type": "IsolationForest",
        "trained_at": artifact.get("trained_at"),
        "segment_count": artifact.get("segment_count", 0),
    }


def fallback_propensity(segment) -> float:
    stored = getattr(segment, "ml_static_propensity", None)
    if stored is not None:
        return clamp(float(stored), 0.0, 1.0)
    return clamp(float(getattr(segment, "drainage_proxy", 0.5) or 0.5), 0.0, 1.0)


def predict_static_propensity(segment) -> float:
    scores = predict_all([segment])
    return scores.get(int(getattr(segment, "id", 0)), fallback_propensity(segment))


def predict_all(segments: list) -> dict[int, float]:
    if not segments:
        return {}
    artifact = load_artifact()
    if artifact is None:
        return {int(segment.id): fallback_propensity(segment) for segment in segments}

    try:
        features = [segment_features(segment) for segment in segments]
        scaled = artifact["scaler"].transform(features)
        raw_scores = artifact["model"].score_samples(scaled)
        score_min = artifact.get("score_min")
        score_max = artifact.get("score_max")
        if score_min is None or score_max is None:
            score_min = float(min(raw_scores))
            score_max = float(max(raw_scores))
        span = max(float(score_max) - float(score_min), 1e-9)
        expected = artifact.get("feature_names") or FEATURE_NAMES
        if list(expected) != FEATURE_NAMES:
            logger.warning("Model feature names differ from current FEATURE_NAMES; scoring anyway.")
        return {
            int(segment.id): clamp(1.0 - ((float(raw) - float(score_min)) / span), 0.0, 1.0)
            for segment, raw in zip(segments, raw_scores)
        }
    except Exception:
        logger.exception("Flood risk model inference failed; using heuristic propensity.")
        return {int(segment.id): fallback_propensity(segment) for segment in segments}
