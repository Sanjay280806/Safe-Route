from datetime import timezone

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import User
from app.schemas import (
    ActiveReportResponse,
    BlockedReportRequest,
    BlockedReportResponse,
    RoadStatus,
    VerifyReportRequest,
)
from app.services import report_service


router = APIRouter(tags=["reports"])


def _isoformat(value) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@router.post("/reports/blocked", response_model=BlockedReportResponse)
def create_blocked_report(
    payload: BlockedReportRequest,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("reporter", "admin")),
) -> BlockedReportResponse:
    report, created = report_service.create_blocked_report(
        db,
        user=user,
        segment_id=payload.segment_id,
        source=payload.source,
        note=payload.note,
        flood_status=payload.flood_status,
    )
    response.status_code = 201 if created else 200
    return BlockedReportResponse(
        report_id=report.id,
        segment_id=report.segment_id,
        verification_status=report.verification_status,
        credibility_score=report.credibility_score,
        road_status=RoadStatus(**report_service.road_status_for(report.segment)),
    )


@router.get("/reports/active", response_model=list[ActiveReportResponse])
def list_active_reports(db: Session = Depends(get_db)) -> list[ActiveReportResponse]:
    reports = report_service.list_active_reports(db)
    items = []
    for report in reports:
        items.append(
            ActiveReportResponse(
                id=report.id,
                segment_id=report.segment_id,
                road_name=report.segment.name if report.segment else None,
                source=report.source,
                verification_status=report.verification_status,
                note=report.note,
                created_at=_isoformat(report.created_at),
            )
        )
    return items


@router.post("/reports/{report_id}/verify", response_model=BlockedReportResponse)
def verify_report(
    report_id: int,
    payload: VerifyReportRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
) -> BlockedReportResponse:
    report = report_service.verify_report(db, user=user, report_id=report_id, decision=payload.decision)
    return BlockedReportResponse(
        report_id=report.id,
        segment_id=report.segment_id,
        verification_status=report.verification_status,
        credibility_score=report.credibility_score,
        road_status=RoadStatus(**report_service.road_status_for(report.segment)),
    )
