from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from sqlalchemy import inspect

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import auth, health, map, meta, pois, reports, scenarios
from app.routers.routes import router as routes_router
from app.services.import_service import import_all
from app.services.seed_service import seed_users
from app.utils.errors import (
    APIError,
    api_error_handler,
    http_exception_handler,
    validation_exception_handler,
)
import app.models  # noqa: F401


def bootstrap_database() -> None:
    inspector = inspect(engine)
    if inspector.has_table("road_segments"):
        columns = {column["name"] for column in inspector.get_columns("road_segments")}
        if "current_risk_score" not in columns:
            Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_users(db)
        import_all(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    bootstrap_database()
    yield


app = FastAPI(
    title="SafeRoute Velachery Benchmark API",
    
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(meta.router, prefix="/api")
app.include_router(scenarios.router, prefix="/api")
app.include_router(pois.router, prefix="/api")
app.include_router(map.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(routes_router, prefix="/api")

bootstrap_database()
