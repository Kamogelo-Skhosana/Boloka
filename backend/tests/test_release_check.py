import json

import httpx
import pytest

from app.forecasting import build_forecast
from app.release_check import (
    CheckFailed,
    Credentials,
    validate_targets,
    verify_accounts,
)

PROJECT = "https://project.example.invalid"
API = "http://localhost:8000/api/v1"
OWNERS = ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"]
KEY = "sb_publishable_test"


def checker(*, leak=False, empty=False, unavailable=False, same=False, bad_forecast=False, cleanup_failure=False, second_login_failure=False):
    calls = []

    def handler(request):
        calls.append(request)
        path = request.url.path
        if path.endswith("/token"):
            email = json.loads(request.content)["email"]
            index = 0 if email == "a@example.invalid" else 1
            if index == 1 and second_login_failure:
                return httpx.Response(401, json={"message": "private diagnostic"})
            return httpx.Response(200, json={"access_token": f"test-token-{index}",
                                            "user": {"id": OWNERS[0 if same else index]}})
        if path.endswith("/logout"):
            assert request.url.params["scope"] == "local"
            return httpx.Response(500 if cleanup_failure else 204)
        if path.startswith("/rest/v1/"):
            assert request.headers["apikey"] == KEY
            return httpx.Response(200, json=[{"id": "foreign"}] if leak else [])
        if unavailable:
            return httpx.Response(503, json={"error": {"message": "Do not echo private details"}})
        index = int(request.headers["authorization"][-1])
        if path.endswith(("/income", "/expenses", "/savings")):
            return httpx.Response(200, json={"items": [] if empty else [{"id": "row", "user_id": OWNERS[index]}]})
        if path.endswith("/forecast"):
            return httpx.Response(200, json={} if bad_forecast else build_forecast([], []))
        return httpx.Response(200, json={"balance_cents": 0})

    return httpx.Client(transport=httpx.MockTransport(handler)), calls


def accounts():
    return [Credentials("a@example.invalid", "unit-test-password-a"),
            Credentials("b@example.invalid", "unit-test-password-b")]


def test_two_account_check_uses_caller_tokens_and_only_reads_financial_records():
    client, calls = checker()
    with client:
        result = verify_accounts(client, API, PROJECT, KEY, accounts())
    assert result == {label: {"income": 1, "expenses": 1, "savings": 1} for label in "AB"}
    data_calls = [r for r in calls if "/auth/v1/" not in r.url.path]
    assert data_calls and all(r.method == "GET" for r in data_calls)
    for r in data_calls:
        assert r.headers["authorization"] in ("Bearer test-token-0", "Bearer test-token-1")
        if "/rest/v1/" in r.url.path:
            index = int(r.headers["authorization"][-1])
            assert r.url.params["user_id"] == "eq." + OWNERS[1 - index]
    assert len([r for r in calls if r.url.path.endswith("/logout")]) == 2


@pytest.mark.parametrize("options,match", [
    ({"leak": True}, "foreign income"),
    ({"empty": True}, "seeded income and expenses"),
    ({"unavailable": True}, "HTTP 503"),
    ({"same": True}, "same account"),
    ({"bad_forecast": True}, "API contract"),
    ({"cleanup_failure": True}, "could not be signed out"),
])
def test_failed_check_never_reports_success_and_cleans_its_sessions(options, match):
    client, calls = checker(**options)
    with client, pytest.raises(CheckFailed, match=match) as exc:
        verify_accounts(client, API, PROJECT, KEY, accounts())
    assert "private details" not in str(exc.value)
    assert len([r for r in calls if r.url.path.endswith("/logout")]) == 2


def test_second_signin_failure_cleans_first_session_without_echoing_auth_body():
    client, calls = checker(second_login_failure=True)
    with client, pytest.raises(CheckFailed, match="Account B sign-in failed") as exc:
        verify_accounts(client, API, PROJECT, KEY, accounts())
    assert "private diagnostic" not in str(exc.value)
    assert len([r for r in calls if r.url.path.endswith("/logout")]) == 1
    assert not any(r.url.path.startswith("/api/v1") for r in calls)


@pytest.mark.parametrize("api,project,key", [
    ("http://public.example.invalid/api/v1", PROJECT, KEY),
    (API, "http://project.example.invalid", KEY),
    (API, PROJECT, "sb_secret_privileged-test"),
    ("https://user:password@example.invalid/api/v1", PROJECT, KEY),
    (API, PROJECT + "?private=value", KEY),
])
def test_rejects_unsafe_targets_before_credentials_are_sent(api, project, key):
    with pytest.raises(CheckFailed):
        validate_targets(api, project, key)


def test_credential_representation_does_not_disclose_values():
    value = repr(accounts()[0])
    assert "unit-test-password" not in value
    assert "example.invalid" not in value


def test_write_mode_runs_after_reads_and_before_session_logout(monkeypatch):
    from app import release_check

    client, calls = checker()
    def writes(client_arg, api, project, key, sessions, marker, protected_ids):
        assert client_arg is client
        assert (api, project, key) == (API, PROJECT, KEY)
        assert len(sessions) == 2
        assert marker.startswith("Boloka isolation QA ")
        assert protected_ids == {"row"}
        assert not any(r.url.path.endswith("/logout") for r in calls)
        raise release_check.WriteCheckFailed("Safe mutation failure")
    monkeypatch.setattr(release_check, "verify_mutations", writes)
    with client, pytest.raises(CheckFailed, match="Safe mutation failure"):
        verify_accounts(client, API, PROJECT, KEY, accounts(), check_writes=True)
    assert len([r for r in calls if r.url.path.endswith("/logout")]) == 2
