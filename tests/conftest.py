import pytest
from fastapi.testclient import TestClient

from main import app
from app.services.auth import reset_tokens
from app.storage import reset_all


@pytest.fixture(autouse=True)
def _clean_state():
    """Every test starts with empty in-memory storage — no cross-test leakage."""
    reset_all()
    reset_tokens()
    yield
    reset_all()
    reset_tokens()


@pytest.fixture
def client():
    return TestClient(app)
