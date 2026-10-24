from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

from app import database
from app.config import settings
from app.main import app

USER = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
PROJECT = "https://project.example.invalid"
TEST_SECRET = "local-unit-test-only-signing-key-not-a-deployed-secret"


def token(**changes):
    claims = {"sub": USER, "role": "authenticated", "aud": "authenticated",
              "iss": PROJECT + "/auth/v1", "exp": datetime.now(UTC) + timedelta(minutes=5)}
    claims.update(changes)
    return jwt.encode(claims, TEST_SECRET, algorithm="HS256")


@pytest.fixture
def configured_auth(monkeypatch):
    monkeypatch.setattr(settings, "supabase_url", PROJECT)
    monkeypatch.setattr(settings, "supabase_jwt_secret", TEST_SECRET)
    monkeypatch.setattr(settings, "supabase_publishable_key", "sb_publishable_unit-test")
    return TestClient(app)


@pytest.mark.parametrize("changes", [
    {"role": "service_role"}, {"role": "anon"}, {"role": None},
    {"sub": "not-a-uuid"}, {"sub": None},
    {"iss": "https://another-project.invalid/auth/v1"},
    {"aud": "another-audience"},
    {"exp": datetime.now(UTC) - timedelta(minutes=5)},
])
def test_rejects_invalid_or_privileged_identity_before_database(configured_auth, monkeypatch, changes):
    monkeypatch.setattr(database.httpx, "request", lambda *a, **k: pytest.fail("Invalid token reached database"))
    response = configured_auth.get("/api/v1/income", headers={"Authorization": "Bearer " + token(**changes)})
    assert response.status_code == 401


def test_requires_expiry_and_valid_signature(configured_auth):
    claims = {"sub": USER, "aud": "authenticated", "role": "authenticated", "iss": PROJECT + "/auth/v1"}
    for value in [jwt.encode(claims, TEST_SECRET, algorithm="HS256"),
                  jwt.encode({**claims, "exp": datetime.now(UTC) + timedelta(minutes=5)}, "wrong-test-key", algorithm="HS256")]:
        assert configured_auth.get("/api/v1/income", headers={"Authorization": "Bearer " + value}).status_code == 401


@pytest.mark.parametrize("method,path,body", [
    ("GET", "/income", None), ("GET", "/expenses", None), ("GET", "/savings", None),
    ("GET", "/forecast", None), ("GET", "/summary", None),
    ("POST", "/forecast/scenario", {"available_balance_cents": 0}),
    ("POST", "/income", {"amount_cents": 100, "received_on": "2026-10-24"}),
    ("POST", "/expenses", {"amount_cents": 100, "spent_on": "2026-10-24"}),
    ("POST", "/savings", {"amount_cents": 100, "saved_on": "2026-10-24"}),
    ("PATCH", "/income/cccccccc-cccc-cccc-cccc-cccccccccccc", {"note": "fixed"}),
    ("PATCH", "/expenses/cccccccc-cccc-cccc-cccc-cccccccccccc", {"note": "fixed"}),
    ("DELETE", "/income/cccccccc-cccc-cccc-cccc-cccccccccccc", None),
    ("DELETE", "/expenses/cccccccc-cccc-cccc-cccc-cccccccccccc", None),
    ("DELETE", "/savings/cccccccc-cccc-cccc-cccc-cccccccccccc", None),
])
def test_every_data_endpoint_forwards_the_verified_caller(configured_auth, monkeypatch, method, path, body):
    calls = []
    access_token = token()

    def request(verb, url, **kwargs):
        import httpx
        calls.append(kwargs)
        return httpx.Response(200, json=[] if verb == "GET" else [{"id": USER}])

    monkeypatch.setattr(database.httpx, "request", request)
    response = configured_auth.request(method, "/api/v1" + path, json=body,
                                       headers={"Authorization": "Bearer " + access_token})
    assert response.status_code in (200, 201, 204)
    assert calls
    assert all(call["headers"]["Authorization"] == "Bearer " + access_token for call in calls)
    assert all(call["headers"]["apikey"] == "sb_publishable_unit-test" for call in calls)


def test_csv_import_forwards_caller_and_assigns_verified_owner(configured_auth, monkeypatch):
    calls = []

    def request(*args, **kwargs):
        import httpx
        calls.append(kwargs)
        return httpx.Response(201)

    monkeypatch.setattr(database.httpx, "request", request)
    access_token = token()
    response = configured_auth.post("/api/v1/income/import", headers={"Authorization": "Bearer " + access_token},
                                    files={"file": ("history.csv", b"amount,source,received_on\n10,Test,2026-10-24\n", "text/csv")})
    assert response.status_code == 200
    assert calls[0]["headers"]["Authorization"] == "Bearer " + access_token
    assert calls[0]["json"][0]["user_id"] == USER
