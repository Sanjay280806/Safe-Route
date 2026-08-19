from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Poi
from app.schemas import PoiResponse
from app.utils.errors import APIError


router = APIRouter(tags=["pois"])


def _to_response(poi: Poi) -> PoiResponse:
    return PoiResponse(
        id=poi.id,
        external_id=poi.external_id,
        name=poi.name,
        category=poi.category,
        lat=poi.lat,
        lon=poi.lon,
        address=poi.address,
        phone=poi.phone,
        status=poi.status,
        nearest_node_id=poi.nearest_node_id,
        source=poi.source,
        notes=poi.notes,
    )


@router.get("/pois", response_model=list[PoiResponse])
def list_pois(
    db: Session = Depends(get_db),
    category: str | None = Query(default=None),
    q: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> list[PoiResponse]:
    query = db.query(Poi)
    if category:
        query = query.filter(Poi.category == category)
    if status:
        query = query.filter(Poi.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter((Poi.name.ilike(like)) | (Poi.address.ilike(like)) | (Poi.category.ilike(like)))
    return [_to_response(poi) for poi in query.order_by(Poi.id).all()]


@router.get("/pois/{poi_id}", response_model=PoiResponse)
def get_poi(poi_id: int, db: Session = Depends(get_db)) -> PoiResponse:
    poi = db.query(Poi).filter(Poi.id == poi_id).one_or_none()
    if poi is None:
        raise APIError(404, "POI_NOT_FOUND", "POI was not found.")
    return _to_response(poi)
