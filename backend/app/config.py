from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"
MOCK_DATA_DIR = DATA_DIR / "mock"
VELACHERY_DATA_DIR = DATA_DIR / "velachery"
MODEL_DIR = PROJECT_DIR / "models"
MODEL_PATH = MODEL_DIR / "risk_model.joblib"
MODEL_META_PATH = MODEL_DIR / "model_meta.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_DIR / ".env", extra="ignore")

    app_env: str = "development"
    secret_key: str = "change-me"
    database_url: str = "sqlite:///./saferoute.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    default_lat: float = 12.981
    default_lon: float = 80.213
    area_name: str = "West Velachery, Chennai"
    model_path: str = str(MODEL_PATH)
    snap_radius_meters: int = 250
    blocked_penalty: float = 1_000_000.0
    risk_ml_weight: float = 0.45
    risk_rule_weight: float = 0.55
    max_route_alternatives: int = 3
    auth_admin_username: str | None = None
    auth_admin_password: str | None = None
    auth_reporter_username: str | None = None
    auth_reporter_password: str | None = None
    auth_responder_username: str | None = None
    auth_responder_password: str | None = None
    seed_placeholder_shelters: bool = True
    jwt_expire_seconds: int = 43200

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.app_env == "production" and settings.secret_key in {"", "change-me"}:
        raise RuntimeError("SECRET_KEY must be set to a strong value in production.")
    return settings


settings = get_settings()

DATABASE_URL = settings.database_url
SNAP_RADIUS_METERS = float(settings.snap_radius_meters)
DEFAULT_SPEED_MPS = 4.5
BLOCKED_PENALTY = settings.blocked_penalty
