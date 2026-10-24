from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_protected_requires_auth():
    # No Authorization header, so a protected endpoint must be rejected.
    res = client.get("/api/v1/summary")
    assert res.status_code in (401, 403)
