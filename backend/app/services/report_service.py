from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import AuditLog, BlockedReport, RoadSegment, Scenario, User
from app.utils.errors import APIError
from app.utils.geo_math import risk_level_for_score


SOURCE_WEIGHTS = {
    "control_room": 1.0,
    "field_official": 0.9,
    "trusted_volunteer": 0.75,
    "ai_prediction": 0.65,
    "citizen": 0.4,
    "responder": 0.9,
}


def create_blocked_report(
    db: Session,
    user: User,
    segment_id: int,
    source: str,
    note: str | None,
    flood_status: str,
) -> tuple[BlockedReport, bool]:
    segment = db.query(RoadSegment).filter(RoadSegment.id == segment_id).one_or_none()
    if segment is None:
        raise APIError(404, "SEGMENT_NOT_FOUND", "Road segment was not found.")

    existing = (
        db.query(BlockedReport)
        .filter(BlockedReport.segment_id == segment_id, BlockedReport.status == "active")
        .one_or_none()
    )
    if existing is not None:
        return existing, False

    score = _credibility_score(db, segment, source)
    verification = _verification_status(score, source)
    report = BlockedReport(
        segment_id=segment.id,
        user_id=user.id,
        source=source,
        note=note,
        status="active",
        verification_status=verification,
        credibility_score=round(score, 2),
        flood_status=flood_status,
    )
    db.add(report)
    db.flush()
    _apply_report_to_segment(segment, report)
    _write_audit(db, user.id, "create_blocked_report", "blocked_report", report.id, {"segment_id": segment.id})
    db.commit()
    db.refresh(report)
    db.refresh(segment)
    return report, True


def verify_report(db: Session, user: User, report_id: int, decision: str) -> BlockedReport:
    report = db.query(BlockedReport).filter(BlockedReport.id == report_id).one_or_none()
    if report is None:
        raise APIError(404, "REPORT_NOT_FOUND", "Report was not found.")
    segment = db.query(RoadSegment).filter(RoadSegment.id == report.segment_id).one()

    if decision == "confirm":
        report.verification_status = "confirmed"
        report.status = "active"
        report.flood_status = report.flood_status or "confirmed_flooded"
        _apply_report_to_segment(segment, report)
    else:
        report.verification_status = "rejected"
        report.status = "rejected"
        report.resolved_at = datetime.now(timezone.utc)
        _refresh_segment_from_reports(db, segment)

    _write_audit(db, user.id, "verify_report", "blocked_report", report.id, {"decision": decision})
    db.commit()
    db.refresh(report)
    return report


def list_active_reports(db: Session) -> list[BlockedReport]:
    return (
        db.query(BlockedReport)
        .filter(BlockedReport.status == "active")
        .order_by(BlockedReport.created_at.desc())
        .all()
    )


def road_status_for(segment: RoadSegment) -> dict:
    return {
        "blocked": bool(segment.blocked),
        "flood_status": segment.flood_status,
        "current_risk_level": segment.current_risk_level,
    }


def _apply_report_to_segment(segment: RoadSegment, report: BlockedReport) -> None:
    segment.active_report_count = max(segment.active_report_count, 1)
    if report.verification_status == "confirmed":
        segment.blocked = 1
        segment.flood_status = report.flood_status or "confirmed_flooded"
        segment.current_risk_score = 1.0
        segment.current_risk_level = "critical"
        segment.predicted_time_to_high_risk_min = 0
    elif report.verification_status == "pending":
        if not segment.blocked:
            segment.flood_status = report.flood_status or "possible_risk"
            segment.current_risk_score = max(segment.current_risk_score, 0.55)
            segment.current_risk_level = risk_level_for_score(segment.current_risk_score)


def _refresh_segment_from_reports(db: Session, segment: RoadSegment) -> None:
    remaining = (
        db.query(BlockedReport)
        .filter(
            BlockedReport.segment_id == segment.id,
            BlockedReport.status == "active",
            BlockedReport.verification_status == "confirmed",
        )
        .count()
    )
    pending = (
        db.query(BlockedReport)
        .filter(
            BlockedReport.segment_id == segment.id,
            BlockedReport.status == "active",
            BlockedReport.verification_status == "pending",
        )
        .count()
    )
    segment.active_report_count = remaining + pending
    if remaining == 0:
        segment.blocked = 0
        if pending == 0:
            segment.flood_status = "safe"
            segment.current_risk_score = min(segment.current_risk_score, 0.24)
            segment.current_risk_level = risk_level_for_score(segment.current_risk_score)


def _credibility_score(db: Session, segment: RoadSegment, source: str) -> float:
    source_weight = SOURCE_WEIGHTS.get(source, 0.4)
    historical = 1.0 if segment.historical_flood_count > 0 else 0.3
    scenario = db.query(Scenario).filter(Scenario.is_active == 1).first()
    rainfall = scenario.rainfall_mm_24h if scenario is not None else 0.0
    weather = 1.0 if rainfall >= 80 else 0.4
    nearby = (
        db.query(BlockedReport)
        .filter(BlockedReport.segment_id == segment.id)
        .count()
    )
    duplicate = 1.0 if nearby else 0.2
    return max(
        0.0,
        min(1.0, 0.50 * source_weight + 0.20 * historical + 0.20 * weather + 0.10 * duplicate),
    )


def _verification_status(score: float, source: str) -> str:
    if score >= 0.75 or source in {"control_room", "field_official"}:
        return "confirmed"
    return "pending"


def _write_audit(db: Session, user_id: int | None, action: str, entity_type: str, entity_id: int | None, payload: dict) -> None:
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            payload_json=json.dumps(payload),
        )
    )
