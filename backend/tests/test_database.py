import httpx
import jwt
import pytest
from fastapi import HTTPException

from app import database


def test_reads_continue_after_short_pages_and_preserve_ownership(monkeypatch):
    monkeypatch.setattr(database.settings, "supabase_url", "https://example.invalid")
    monkeypatch.setattr(database.settings, "supabase_publishable_key", "sb_publishable_test-only")
    calls = []
    pages = iter([[{"id": "a"}, {"id": "b"}], [{"id": "c"}], []])

    def request(*args, **kwargs):
        calls.append(kwargs["params"])
        return httpx.Response(200, json=next(pages))

    monkeypatch.setattr(database.httpx, "request", request)
    result = database.request_table("GET", "income_events", user_id="verified-user", access_token="caller-token", params={"order": "received_on.asc"})
    assert [row["id"] for row in result] == ["a", "b", "c"]
    assert [call["offset"] for call in calls] == ["0", "2", "3"]
    assert all(call["user_id"] == "eq.verified-user" for call in calls)
    assert all(call["order"] == "received_on.asc,id.asc" for call in calls)


@pytest.mark.parametrize("key", ["sb_secret_test-only", jwt.encode({"role": "service_role"}, "unit-test", algorithm="HS256"), ""])
def test_privileged_or_missing_project_key_fails_closed(monkeypatch, key):
    monkeypatch.setattr(database.settings, "supabase_url", "https://example.invalid")
    monkeypatch.setattr(database.settings, "supabase_publishable_key", key)
    monkeypatch.setattr(database.httpx, "request", lambda *a, **k: pytest.fail("Privileged key must not reach Supabase"))
    with pytest.raises(HTTPException) as error:
        database.request_table("GET", "income_events", user_id="verified-user", access_token="caller-token")
    assert error.value.status_code == 503


def test_legacy_anon_key_uses_user_token_for_authorization(monkeypatch):
    key = jwt.encode({"role": "anon"}, "unit-test", algorithm="HS256")
    monkeypatch.setattr(database.settings, "supabase_url", "https://example.invalid")
    monkeypatch.setattr(database.settings, "supabase_publishable_key", key)

    def request(*args, **kwargs):
        assert kwargs["headers"]["apikey"] == key
        assert kwargs["headers"]["Authorization"] == "Bearer caller-token"
        return httpx.Response(200, json=[])

    monkeypatch.setattr(database.httpx, "request", request)
    assert database.request_table("GET", "income_events", user_id="verified-user", access_token="caller-token") == []
