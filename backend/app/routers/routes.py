from fastapi import APIRouter, Depends, HTTPException
from typing import Any

from app.database import get_db
from app.repositories.benchmark_repository import BenchmarkRepository
from app.schemas import RerouteRequest, RouteRequest, RouteResponse
from app.services.routing_service import (
    DestinationNotFoundError,
    OriginNotSnappableError,
    RouteNotFoundError,
    RoutingService,
)


router = APIRouter(tags=["AI Routing"])


@router.post("/routes", response_model=RouteResponse)
def create_route(payload: RouteRequest, db: Any = Depends(get_db)) -> dict:
    service = RoutingService(BenchmarkRepository(db))
    destination_payload = (
        payload.destination.model_dump()
        if hasattr(payload.destination, "model_dump")
        else payload.destination.dict()
    )
    try:
        return service.create_route(
            origin_lat=payload.origin.lat,
            origin_lon=payload.origin.lon,
            destination=destination_payload,
            route_mode=payload.route_mode,
            scenario_id=payload.scenario_id,
            include_alternatives=payload.include_alternatives,
        )
    except OriginNotSnappableError as exc:
        raise HTTPException(status_code=422, detail={"code": "ORIGIN_NOT_SNAPPABLE", "message": str(exc)})
    except DestinationNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "DESTINATION_NOT_FOUND", "message": str(exc)})
    except RouteNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "ROUTE_NOT_FOUND", "message": str(exc)})


@router.post("/routes/re-route", response_model=RouteResponse)
def reroute(payload: RerouteRequest, db: Any = Depends(get_db)) -> dict:
    route_request = RouteRequest(
        origin=payload.current_location,
        destination=payload.destination,
        route_mode=payload.route_mode,
        scenario_id=payload.scenario_id,
        include_alternatives=payload.include_alternatives,
    )
    return create_route(route_request, db)
