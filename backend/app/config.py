from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"
MOCK_DATA_DIR = DATA_DIR / "mock"
MODEL_DIR = PROJECT_DIR / "models"
MODEL_PATH = MODEL_DIR / "risk_model.joblib"
MODEL_META_PATH = MODEL_DIR / "model_meta.json"

DATABASE_URL = "sqlite:///./saferoute.db"
SNAP_RADIUS_METERS = 250.0
DEFAULT_SPEED_MPS = 4.5
BLOCKED_PENALTY = 1_000_000.0
