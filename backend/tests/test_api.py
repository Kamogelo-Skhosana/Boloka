from uuid import UUID

from fastapi.testclient import TestClient

from app import routers
from app.auth import get_current_user_id
from app.main import app

USER_ID = "22eea3e4-4317-4794-93ec-2d5b18fcb67a"


def test_health_is_public():
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_protected_routes_reject_missing_token():
    response = TestClient(app).get("/api/v1/income")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthenticated"


def test_create_income_uses_verified_user_not_body_user(monkeypatch):
    app.dependency_overrides[get_current_user_id] = lambda: USER_ID
    calls = []

    def fake_request(method, table, **kwargs):
        calls.append((method, table, kwargs))
        return [{"id": "income-id", **kwargs["payload"]}]

    monkeypatch.setattr(routers, "request_table", fake_request)
    try:
        response = TestClient(app).post(
            "/api/v1/income",
            json={
                "amount_cents": 12050,
                "source": "Market stall",
                "received_on": "2026-10-24",
                "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            },
            headers={"Authorization": "Bearer test-token"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert calls[0][2]["payload"]["user_id"] == str(UUID(USER_ID))
    assert response.json()["amount_cents"] == 12050


def test_invalid_income_is_reported_as_validation_error():
    app.dependency_overrides[get_current_user_id] = lambda: USER_ID
    try:
        response = TestClient(app).post(
            "/api/v1/income",
            json={"amount_cents": -1, "received_on": "not-a-date"},
            headers={"Authorization": "Bearer test-token"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
