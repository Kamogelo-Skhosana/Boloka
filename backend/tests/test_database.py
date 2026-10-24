import httpx

from app import database


def test_reads_continue_after_short_pages_and_preserve_ownership(monkeypatch):
    monkeypatch.setattr(database.settings, "supabase_url", "https://example.invalid")
    monkeypatch.setattr(database.settings, "supabase_service_role_key", "test-only")
    calls = []
    pages = iter([[{"id": "a"}, {"id": "b"}], [{"id": "c"}], []])

    def request(*args, **kwargs):
        calls.append(kwargs["params"])
        return httpx.Response(200, json=next(pages))

    monkeypatch.setattr(database.httpx, "request", request)
    result = database.request_table("GET", "income_events", user_id="verified-user", params={"order": "received_on.asc"})
    assert [row["id"] for row in result] == ["a", "b", "c"]
    assert [call["offset"] for call in calls] == ["0", "2", "3"]
    assert all(call["user_id"] == "eq.verified-user" for call in calls)
    assert all(call["order"] == "received_on.asc,id.asc" for call in calls)
