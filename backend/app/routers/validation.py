from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ValidationSummaryResponse
from app.services.risk_recompute_service import validation_summary


router = APIRouter(tags=["risk"])


@router.get("/validation/summary", response_model=ValidationSummaryResponse)
def get_validation_summary(db: Session = Depends(get_db)) -> dict:
    return validation_summary(db)
