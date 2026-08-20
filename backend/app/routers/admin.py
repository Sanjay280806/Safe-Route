from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import User
from app.schemas import RecomputeRiskResponse
from app.services.risk_recompute_service import recompute_active_scenario_risk


router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/recompute-risk", response_model=RecomputeRiskResponse)
def recompute_risk(
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("admin")),
) -> dict:
    return recompute_active_scenario_risk(db)
