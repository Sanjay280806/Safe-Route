from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import Scenario, User
from app.schemas import RainfallResponse, RainfallUpdateRequest, RecomputeRiskResponse
from app.services.risk_recompute_service import recompute_risk
from app.utils.errors import APIError


router = APIRouter(tags=["admin"])


def _active_scenario(db: Session) -> Scenario:
    scenario = db.query(Scenario).filter(Scenario.is_active == 1).first()
    if scenario is None:
        raise APIError(404, "SCENARIO_NOT_FOUND", "No active rainfall scenario is available.")
    return scenario


@router.post("/admin/recompute-risk", response_model=RecomputeRiskResponse)
def recompute_current_risk(
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("admin")),
) -> dict[str, int | bool]:
    return recompute_risk(db)


@router.get("/rainfall/current", response_model=RainfallResponse)
def current_rainfall(db: Session = Depends(get_db)) -> RainfallResponse:
    scenario = _active_scenario(db)
    return RainfallResponse(
        scenario_id=scenario.id,
        scenario_name=scenario.name,
        rainfall_mm_24h=scenario.rainfall_mm_24h,
        rainfall_mm_1h=scenario.rainfall_mm_1h,
        source=scenario.source,
        updated_from="seeded local scenario" if scenario.source != "admin_entered" else "admin-entered local scenario",
    )


@router.put("/admin/rainfall", response_model=RainfallResponse)
def update_rainfall(
    payload: RainfallUpdateRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("admin")),
) -> RainfallResponse:
    scenario = _active_scenario(db)
    scenario.rainfall_mm_24h = payload.rainfall_mm_24h
    scenario.rainfall_mm_1h = payload.rainfall_mm_1h
    scenario.source = "admin_entered"
    if payload.description is not None:
        scenario.description = payload.description
    db.commit()
    recompute_risk(db, scenario.id)
    return RainfallResponse(
        scenario_id=scenario.id,
        scenario_name=scenario.name,
        rainfall_mm_24h=scenario.rainfall_mm_24h,
        rainfall_mm_1h=scenario.rainfall_mm_1h,
        source=scenario.source,
        updated_from="admin-entered local scenario",
    )
