"""AI training and inference utilities for benchmark flood risk."""

from app.ai.predict import (
    fallback_propensity,
    model_is_loaded,
    model_meta,
    predict_all,
    predict_static_propensity,
)

__all__ = [
    "fallback_propensity",
    "model_is_loaded",
    "model_meta",
    "predict_all",
    "predict_static_propensity",
]
