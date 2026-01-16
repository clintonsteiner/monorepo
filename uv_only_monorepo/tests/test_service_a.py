# tests/test_service_a.py
from fastapi.testclient import TestClient
from service_a.main import app


def test_health() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
