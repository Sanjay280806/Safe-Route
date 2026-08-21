from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_optional_user, require_roles
from app.models import FieldMessage, RoadSegment, User
from app.schemas import FieldMessageRequest, FieldMessageResponse, FieldMessageStatusRequest
from app.utils.errors import APIError


router = APIRouter(tags=["messages"])


def _to_response(db: Session, item: FieldMessage) -> FieldMessageResponse:
    road = db.query(RoadSegment).filter(RoadSegment.id == item.segment_id).one_or_none() if item.segment_id else None
    return FieldMessageResponse(
        id=item.id,
        sender_name=item.sender_name,
        sender_role=item.sender_role,
        category=item.category,
        message=item.message,
        segment_id=item.segment_id,
        road_name=road.name if road else None,
        status=item.status,
        created_at=item.created_at.isoformat(),
        updated_at=item.updated_at.isoformat(),
    )


@router.post("/messages", response_model=FieldMessageResponse, status_code=201)
def create_message(
    payload: FieldMessageRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
) -> FieldMessageResponse:
    if payload.segment_id is not None and db.query(RoadSegment).filter(RoadSegment.id == payload.segment_id).one_or_none() is None:
        raise APIError(404, "SEGMENT_NOT_FOUND", "Road segment was not found.")
    item = FieldMessage(
        sender_name=user.username if user else payload.sender_name,
        sender_role=user.role if user else "resident",
        category=payload.category,
        message=payload.message,
        segment_id=payload.segment_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_response(db, item)


@router.get("/messages", response_model=list[FieldMessageResponse])
def list_messages(
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("reporter", "admin")),
) -> list[FieldMessageResponse]:
    messages = db.query(FieldMessage).order_by(FieldMessage.status, FieldMessage.created_at.desc()).all()
    return [_to_response(db, item) for item in messages]


@router.patch("/messages/{message_id}", response_model=FieldMessageResponse)
def update_message_status(
    message_id: int,
    payload: FieldMessageStatusRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("reporter", "admin")),
) -> FieldMessageResponse:
    item = db.query(FieldMessage).filter(FieldMessage.id == message_id).one_or_none()
    if item is None:
        raise APIError(404, "MESSAGE_NOT_FOUND", "Message was not found.")
    item.status = payload.status
    item.handled_by_user_id = user.id
    db.commit()
    db.refresh(item)
    return _to_response(db, item)
