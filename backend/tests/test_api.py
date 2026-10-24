from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app import routers
from app.auth import get_current_user_id
from app.main import app

USER_ID = "22eea3e4-4317-4794-93ec-2d5b18fcb67a"
ENTRY_ID = "3a800bda-00c2-4cfa-9cd6-227357dc1a14"


@pytest.fixture
def authenticated_client():
    app.dependency_overrides[get_current_user_id] = lambda: USER_ID
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("resource,field", [
    ("income", "amount_cents"), ("income", "received_on"),
    ("expenses", "amount_cents"), ("expenses", "spent_on"),
    ("expenses", "recurring"),
])
def test_patch_rejects_null_required_fields(authenticated_client, monkeypatch, resource, field):
    def unexpected_request(*args, **kwargs):
        pytest.fail("Invalid input must not reach the database")

    monkeypatch.setattr(routers, "request_table", unexpected_request)
    response = authenticated_client.patch(f"/api/v1/{resource}/{ENTRY_ID}", json={field: None})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


@pytest.mark.parametrize("resource", ["income", "expenses"])
def test_patch_allows_clearing_optional_note(authenticated_client, monkeypatch, resource):
    calls = []

    def fake_request(method, table, **kwargs):
        calls.append((method, table, kwargs))
        return [{"id": ENTRY_ID, "note": None}]

    monkeypatch.setattr(routers, "request_table", fake_request)
    response = authenticated_client.patch(f"/api/v1/{resource}/{ENTRY_ID}", json={"note": None})
    assert response.status_code == 200
    assert calls[0][2]["payload"] == {"note": None}
    assert calls[0][2]["user_id"] == USER_ID
    assert calls[0][2]["params"] == {"id": f"eq.{ENTRY_ID}"}


@pytest.mark.parametrize("resource,date_field", [("income", "received_on"), ("expenses", "spent_on")])
@pytest.mark.parametrize("query,expected", [
    ("?from=2026-10-01", {"DATE": "gte.2026-10-01"}),
    ("?to=2026-10-24", {"DATE": "lte.2026-10-24"}),
    ("?from=2026-10-01&to=2026-10-24", {"and": "(DATE.gte.2026-10-01,DATE.lte.2026-10-24)"}),
    ("?from=2026-10-24&to=2026-10-24", {"and": "(DATE.gte.2026-10-24,DATE.lte.2026-10-24)"}),
])
def test_list_date_filters(authenticated_client, monkeypatch, resource, date_field, query, expected):
    calls = []

    def fake_request(method, table, **kwargs):
        calls.append((method, table, kwargs))
        return []

    monkeypatch.setattr(routers, "request_table", fake_request)
    response = authenticated_client.get(f"/api/v1/{resource}{query}")
    assert response.status_code == 200
    assert response.json() == {"items": []}
    expected_filters = {key.replace("DATE", date_field): value.replace("DATE", date_field) for key, value in expected.items()}
    assert calls[0][2]["params"] == {"order": f"{date_field}.desc,created_at.desc", **expected_filters}
    assert calls[0][2]["user_id"] == USER_ID


@pytest.mark.parametrize("resource", ["income", "expenses"])
def test_list_rejects_reversed_dates(authenticated_client, monkeypatch, resource):
    def unexpected_request(*args, **kwargs):
        pytest.fail("Invalid input must not reach the database")

    monkeypatch.setattr(routers, "request_table", unexpected_request)
    response = authenticated_client.get(f"/api/v1/{resource}?from=2026-10-24&to=2026-10-01")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


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


def test_forecast_endpoint_exposes_model_and_consistent_totals(authenticated_client, monkeypatch):
    monkeypatch.setattr(routers, "request_table", lambda *args, **kwargs: [])
    response = authenticated_client.get("/api/v1/forecast")
    assert response.status_code == 200
    body = response.json()
    assert body["model"]["method"] == "weighted_average"
    assert body["model"]["reason"] == "insufficient_history"
    assert body["model"]["model_mae_cents"] is None
    assert body["predicted_income_cents"] == sum(week["predicted_income_cents"] for week in body["series"])
    assert body["confidence"] == "low"
