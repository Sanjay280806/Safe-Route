from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Scenario
from app.schemas import ScenarioResponse


router = APIRouter(tags=["scenarios"])


@router.get("/scenarios", response_model=list[ScenarioResponse])
def list_scenarios(db: Session = Depends(get_db)) -> list[ScenarioResponse]:
    scenarios = db.query(Scenario).order_by(Scenario.id).all()
    return [
        ScenarioResponse(
            id=scenario.id,
            name=scenario.name,
            description=scenario.description,
            rainfall_mm_24h=scenario.rainfall_mm_24h,
            rainfall_mm_1h=scenario.rainfall_mm_1h,
            source=scenario.source,
            is_active=bool(scenario.is_active),
        )
        for scenario in scenarios
    ]
