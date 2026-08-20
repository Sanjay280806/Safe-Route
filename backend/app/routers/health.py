from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import MODEL_PATH, settings
from app.database import get_db
from app.models import Poi, RoadSegment, Scenario
from app.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    active = db.query(Scenario).filter(Scenario.is_active == 1).first()
    model_path = Path(settings.model_path or MODEL_PATH)
    return HealthResponse(
        status="ok",
        model_loaded=model_path.exists(),
        active_scenario_id=active.id if active else None,
        road_count=db.query(RoadSegment).count(),
        poi_count=db.query(Poi).count(),
    )
