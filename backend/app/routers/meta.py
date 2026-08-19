from fastapi import APIRouter

from app.config import settings
from app.schemas import AreaMetaResponse


router = APIRouter(tags=["meta"])


@router.get("/meta/area", response_model=AreaMetaResponse)
def area_meta() -> AreaMetaResponse:
    return AreaMetaResponse(
        name=settings.area_name,
        bbox=[12.965, 80.195, 12.995, 80.235],
        default_center=[settings.default_lat, settings.default_lon],
        default_zoom=15,
        disclaimer="Demo decision-support tool. Not an official emergency service.",
    )
