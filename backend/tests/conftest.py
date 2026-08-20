import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB = Path(__file__).with_name("saferoute_test.db")
if TEST_DB.exists():
    TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"

from app.main import app
from app.database import engine


@pytest.fixture(scope="session")
def client():
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        engine.dispose()
        if TEST_DB.exists():
            TEST_DB.unlink()
