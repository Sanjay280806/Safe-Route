from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import Poi, ShelterDetail, User
from app.schemas import ShelterCreateRequest, ShelterOccupancyUpdateRequest, ShelterResponse
from app.services.geo_service import nearest_node
from app.utils.errors import APIError


router = APIRouter(tags=["shelters"])


def _to_response(poi: Poi, detail: ShelterDetail) -> ShelterResponse:
    return ShelterResponse(
        poi_id=poi.id,
        name=poi.name,
        lat=poi.lat,
        lon=poi.lon,
        address=poi.address,
        status=poi.status,
        capacity_assumed=detail.capacity_assumed,
        occupancy_assumed=detail.occupancy_assumed,
        available_capacity=max(detail.capacity_assumed - detail.occupancy_assumed, 0),
        accessible=bool(detail.accessible),
        medical_support=bool(detail.medical_support),
        water_available=bool(detail.water_available),
        source=poi.source,
        notes=poi.notes,
    )


def _detail_or_error(db: Session, poi_id: int) -> tuple[Poi, ShelterDetail]:
    poi = db.query(Poi).filter(Poi.id == poi_id, Poi.category == "shelter").one_or_none()
    if poi is None:
        raise APIError(404, "SHELTER_NOT_FOUND", "Shelter was not found.")
    detail = db.query(ShelterDetail).filter(ShelterDetail.poi_id == poi.id).one_or_none()
    if detail is None:
        detail = ShelterDetail(poi_id=poi.id)
        db.add(detail)
        db.flush()
    return poi, detail


@router.get("/shelters", response_model=list[ShelterResponse])
def list_shelters(db: Session = Depends(get_db)) -> list[ShelterResponse]:
    results: list[ShelterResponse] = []
    for poi in db.query(Poi).filter(Poi.category == "shelter").order_by(Poi.id).all():
        detail = db.query(ShelterDetail).filter(ShelterDetail.poi_id == poi.id).one_or_none()
        if detail is not None:
            results.append(_to_response(poi, detail))
    return results


@router.patch("/shelters/{poi_id}/occupancy", response_model=ShelterResponse)
def update_shelter_occupancy(
    poi_id: int,
    payload: ShelterOccupancyUpdateRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("reporter", "admin")),
) -> ShelterResponse:
    poi, detail = _detail_or_error(db, poi_id)
    detail.occupancy_assumed = payload.occupancy_assumed
    if payload.status is not None:
        poi.status = payload.status
    db.commit()
    db.refresh(poi)
    db.refresh(detail)
    return _to_response(poi, detail)


@router.post("/shelters", response_model=ShelterResponse, status_code=201)
def create_shelter(
    payload: ShelterCreateRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("admin")),
) -> ShelterResponse:
    if payload.occupancy_assumed > payload.capacity_assumed:
        raise APIError(422, "INVALID_OCCUPANCY", "Occupancy cannot exceed shelter capacity.")
    node = nearest_node(db, payload.lat, payload.lon)
    poi = Poi(
        name=payload.name,
        category="shelter",
        lat=payload.lat,
        lon=payload.lon,
        address=payload.address or "",
        status="open",
        nearest_node_id=node.id if node else None,
        source="user_supplied_unverified",
        notes="User-supplied shelter. Verify before operational use.",
    )
    db.add(poi)
    db.flush()
    detail = ShelterDetail(
        poi_id=poi.id,
        capacity_assumed=payload.capacity_assumed,
        occupancy_assumed=payload.occupancy_assumed,
        accessible=1 if payload.accessible else 0,
        medical_support=1 if payload.medical_support else 0,
        water_available=1 if payload.water_available else 0,
    )
    db.add(detail)
    db.commit()
    db.refresh(poi)
    db.refresh(detail)
    return _to_response(poi, detail)
