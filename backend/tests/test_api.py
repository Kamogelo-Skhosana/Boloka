from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app import routers
from app.auth import get_current_access_token, get_current_user_id
from app.main import app

USER_ID = "22eea3e4-4317-4794-93ec-2d5b18fcb67a"
ENTRY_ID = "3a800bda-00c2-4cfa-9cd6-227357dc1a14"


@pytest.fixture
def authenticated_client():
    app.dependency_overrides[get_current_user_id] = lambda: USER_ID
    app.dependency_overrides[get_current_access_token] = lambda: "test-user-access-token"
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
    app.dependency_overrides[get_current_access_token] = lambda: "test-user-access-token"
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
    app.dependency_overrides[get_current_access_token] = lambda: "test-user-access-token"
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
    assert body["model"]["method"] == "pandas_weekly_mean"
    assert body["model"]["reason"] == "unvalidated_baseline"
    assert body["shortfall"]["date"] is None
    assert body["predicted_income_cents"] == sum(week["predicted_income_cents"] for week in body["series"])
    assert body["confidence"] == "low"


@pytest.mark.parametrize("balance", [-1, 1.5, True, 2_000_000_001])
def test_cash_scenario_rejects_invalid_inputs(authenticated_client, balance):
    response = authenticated_client.post("/api/v1/forecast/scenario", json={"available_balance_cents": balance})
    assert response.status_code == 422


def test_cash_scenario_is_not_persisted(authenticated_client, monkeypatch):
    calls = []

    def fake_request(method, table, **kwargs):
        calls.append((method, table))
        return []

    monkeypatch.setattr(routers, "request_table", fake_request)
    response = authenticated_client.post("/api/v1/forecast/scenario", json={"available_balance_cents": 10000})
    assert response.status_code == 200
    assert response.json()["available_balance_cents"] == 10000
    assert all(method == "GET" for method, _ in calls)


def test_cash_scenario_requires_authentication():
    response = TestClient(app).post("/api/v1/forecast/scenario", json={"available_balance_cents": 1000})
    assert response.status_code == 401


def test_forecast_routes_publish_the_same_typed_response_contract():
    schema = app.openapi()
    for path, method in [("/api/v1/forecast", "get"), ("/api/v1/forecast/scenario", "post")]:
        response_schema = schema["paths"][path][method]["responses"]["200"]["content"]["application/json"]["schema"]
        assert response_schema == {"$ref": "#/components/schemas/ForecastResponse"}


def test_forecast_contract_keeps_unknown_and_known_zero_cash_distinct(authenticated_client, monkeypatch):
    monkeypatch.setattr(routers, "request_table", lambda *a, **kw: [])
    unknown = authenticated_client.get("/api/v1/forecast").json()
    zero = authenticated_client.post("/api/v1/forecast/scenario", json={"available_balance_cents": 0}).json()
    assert unknown["available_balance_cents"] is None
    assert zero["available_balance_cents"] == 0
    assert unknown["shortfall"]["date"] is zero["shortfall"]["date"] is None
    assert unknown["series"] == zero["series"] == []
    assert "check_available_cash" in unknown["next_steps"]
    assert "check_available_cash" not in zero["next_steps"]


@pytest.mark.parametrize("path,method", [("/forecast", "get"), ("/forecast/scenario", "post")])
def test_forecast_database_failure_is_not_replaced_with_sample_data(authenticated_client, monkeypatch, path, method):
    from fastapi import HTTPException

    def unavailable(*args, **kwargs):
        raise HTTPException(status_code=502, detail={"error": {"code": "database_unavailable", "message": "Could not reach the database"}})

    monkeypatch.setattr(routers, "request_table", unavailable)
    options = {"json": {}} if method == "post" else {}
    response = getattr(authenticated_client, method)("/api/v1" + path, **options)
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "database_unavailable"
    assert "series" not in response.json()


@pytest.mark.parametrize("resource", ["income", "expenses"])
@pytest.mark.parametrize("method", ["patch", "delete"])
def test_entry_mutation_is_owner_scoped_and_handles_not_found(authenticated_client, monkeypatch, resource, method):
    calls = []

    def fake_request(*args, **kwargs):
        calls.append(kwargs)
        return []

    monkeypatch.setattr(routers, "request_table", fake_request)
    options = {"json": {"amount_cents": 1000}} if method == "patch" else {}
    response = getattr(authenticated_client, method)(f"/api/v1/{resource}/{ENTRY_ID}", **options)
    assert response.status_code == 404
    assert calls[0]["user_id"] == USER_ID
    assert calls[0]["params"]["id"] == f"eq.{ENTRY_ID}"


@pytest.mark.parametrize("populated", [False, True])
def test_dashboard_reuses_three_owner_reads_and_matches_existing_routes(authenticated_client, monkeypatch, populated):
    from datetime import date

    from app import forecasting

    monkeypatch.setattr(routers, "local_today", lambda: date(2026, 10, 25))
    monkeypatch.setattr(forecasting, "local_today", lambda: date(2026, 10, 25))
    records = {
        "income_events": [
            {"id": ENTRY_ID, "amount_cents": 10000, "received_on": "2026-10-20"},
            {"id": "old", "amount_cents": 20000, "received_on": "2026-09-01"},
            {"id": "future", "amount_cents": 99999, "received_on": "2026-10-26"},
        ] if populated else [],
        "expenses": [
            {"id": "paid", "amount_cents": 5000, "spent_on": "2026-10-20", "recurring": False},
            {"id": "due", "amount_cents": 3000, "spent_on": "2026-11-01", "recurring": True},
        ] if populated else [],
        "savings_contributions": [
            {"id": "saved", "amount_cents": 1000, "saved_on": "2026-10-24"},
            {"id": "future", "amount_cents": 9999, "saved_on": "2026-10-26"},
        ] if populated else [],
    }
    calls = []

    def fake_request(method, table, **kwargs):
        calls.append((method, table, kwargs))
        return records[table]

    monkeypatch.setattr(routers, "request_table", fake_request)
    response = authenticated_client.get("/api/v1/dashboard")
    assert response.status_code == 200
    result = response.json()
    assert len(calls) == 3
    assert [c[1] for c in calls] == ["income_events", "expenses", "savings_contributions"]
    for method, _, options in calls:
        assert method == "GET"
        assert options["user_id"] == USER_ID
        assert options["access_token"] == "test-user-access-token"
        assert options["params"]["order"].endswith(".desc,created_at.desc")
    assert result["summary"] == authenticated_client.get("/api/v1/summary").json()
    legacy_forecast = authenticated_client.get("/api/v1/forecast").json()
    # Separate requests have independent generation timestamps, not different estimates.
    assert result["forecast"].pop("generated_at")
    assert legacy_forecast.pop("generated_at")
    assert result["forecast"] == legacy_forecast
    for key, path in [("income", "income"), ("expenses", "expenses"), ("savings", "savings")]:
        assert result[key] == authenticated_client.get("/api/v1/" + path).json()["items"]
    if populated:
        assert result["summary"]["balance_cents"] == 25000
        assert result["summary"]["this_week_income_cents"] == 10000
        assert result["summary"]["set_aside_progress_cents"] == 1000
    assert result["forecast"]["available_balance_cents"] is None


def test_dashboard_requires_authentication():
    assert TestClient(app).get("/api/v1/dashboard").status_code == 401


def test_dashboard_does_not_return_partial_or_fictional_data(authenticated_client, monkeypatch):
    from fastapi import HTTPException

    def fail_second_read(method, table, **kwargs):
        if table == "expenses":
            raise HTTPException(status_code=502, detail="Database unavailable")
        return []

    monkeypatch.setattr(routers, "request_table", fail_second_read)
    response = authenticated_client.get("/api/v1/dashboard")
    assert response.status_code == 502
    assert "summary" not in response.json()
    assert "income" not in response.json()
