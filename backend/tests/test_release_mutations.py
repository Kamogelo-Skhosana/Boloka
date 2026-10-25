import copy
import json
from uuid import NAMESPACE_DNS, uuid4, uuid5

import httpx
import pytest

from app.release_mutations import RESOURCES, WriteCheckFailed, verify_mutations

API = "https://api.example.invalid/api/v1"
PROJECT = "https://project.example.invalid"
KEY = "sb_publishable_fixture"
OWNERS = ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"]
SESSIONS = [(owner, f"fixture-token-{index}") for index, owner in enumerate(OWNERS)]
MARKER = "Boloka isolation QA 11111111-2222-4333-8444-555555555555"


class MutationFixture:
    def __init__(self, failure=None, *, cleanup_failure=False, cap=False):
        self.failure = failure
        self.cleanup_failure = cleanup_failure
        self.cap = cap
        self.calls = []
        self.rows = {table: {str(uuid5(NAMESPACE_DNS, table + owner)): {
            "id": str(uuid5(NAMESPACE_DNS, table + owner)), "user_id": owner,
            "amount_cents": 500, "note": "Existing user record", date_field: "2026-10-24",
        } for owner in OWNERS} for _, table, date_field in RESOURCES}
        self.before = copy.deepcopy(self.rows)
        self.protected = {entry_id for rows in self.rows.values() for entry_id in rows}

    def handler(self, request):
        self.calls.append(request)
        index = int(request.headers["authorization"][-1])
        owner = OWNERS[index]
        parts = request.url.path.strip("/").split("/")
        api = parts[0] == "api"
        if api:
            resource = parts[2]
            table = next(table for name, table, _ in RESOURCES if name == resource)
            entry_id = parts[3] if len(parts) == 4 else None
        else:
            assert request.headers["apikey"] == KEY
            table, entry_id = parts[2], None
        rows = self.rows[table]
        body = json.loads(request.content) if request.content else {}
        if request.method == "POST":
            if not api and body["user_id"] != owner and self.failure != "db_spoof_insert":
                return httpx.Response(403, json={"code": "42501", "message": "private detail"})
            entry_id = body.get("id", str(uuid4()))
            actual_owner = body.get("user_id") if not api or self.failure == "api_owner" else owner
            if api and self.failure == "api_reuses_seed":
                entry_id = next(key for key, value in rows.items() if value["user_id"] == owner)
            row = body | {"id": entry_id, "user_id": actual_owner}
            rows[entry_id] = row
            if api and self.failure == "api_timeout":
                raise httpx.ReadTimeout("private timeout detail", request=request)
            if api and self.failure == "api_error":
                return httpx.Response(500, json={"error": "private response detail"})
            return httpx.Response(201, json=row if api else [row])
        selected = [row for row in rows.values() if (entry_id is None or row["id"] == entry_id)]
        if not api:
            for key, value in request.url.params.items():
                if key in ("id", "user_id", "note"):
                    assert value.startswith("eq.")
                    selected = [row for row in selected if row.get(key) == value[3:]]
        if request.method == "GET":
            selected = [row for row in selected if row["user_id"] == owner]
            if self.cap and "note" in request.url.params:
                selected = selected[:1]
            return httpx.Response(200, json=copy.deepcopy(selected))
        foreign = any(row["user_id"] != owner for row in selected)
        if api and foreign:
            if self.failure == "api_silent_update" and request.method == "PATCH":
                selected[0].update(body)
            if self.failure == "api_silent_delete" and request.method == "DELETE":
                rows.pop(selected[0]["id"])
            return httpx.Response(404, json={"error": "private detail"})
        if not api and foreign:
            if self.failure == "db_silent_update" and request.method == "PATCH":
                selected[0].update(body)
            if self.failure == "db_silent_delete" and request.method == "DELETE":
                rows.pop(selected[0]["id"])
            return httpx.Response(200, json=[])
        if request.method == "PATCH":
            if not api and self.failure == "own_update_denied":
                return httpx.Response(403, json={"code": "42501"})
            if "user_id" in body and body["user_id"] != owner and self.failure != "owner_transfer":
                return httpx.Response(403, json={"code": "42501"})
            for row in selected:
                row.update(body)
            return httpx.Response(200, json=copy.deepcopy(selected[0] if api else selected))
        if request.method == "DELETE":
            if self.cleanup_failure and "note" in request.url.params:
                return httpx.Response(500, json={"error": "private cleanup detail"})
            for row in selected:
                rows.pop(row["id"])
            return httpx.Response(204) if api else httpx.Response(200, json=copy.deepcopy(selected))
        pytest.fail("Unexpected fixture request")

    def run(self):
        with httpx.Client(transport=httpx.MockTransport(self.handler)) as client:
            verify_mutations(client, API, PROJECT, KEY, SESSIONS, MARKER, self.protected)


def test_bidirectional_probes_touch_only_new_rows_and_restore_the_dataset():
    fixture = MutationFixture()
    fixture.run()
    assert fixture.rows == fixture.before
    creates = [request for request in fixture.calls if request.method == "POST" and "/api/v1/" in request.url.path]
    assert len(creates) == 6
    for request in creates:
        index = int(request.headers["authorization"][-1])
        assert json.loads(request.content)["user_id"] == OWNERS[1 - index]
    for request in fixture.calls:
        if request.method in ("PATCH", "DELETE"):
            entry_id = request.url.params.get("id", "eq." + request.url.path.rsplit("/", 1)[-1])[3:]
            assert entry_id not in fixture.protected
    assert len([r for r in fixture.calls if r.method == "PATCH" and "/api/v1/" in r.url.path]) == 8


@pytest.mark.parametrize("failure", ["api_owner", "api_error", "api_silent_update", "api_silent_delete",
                                     "db_silent_update", "db_silent_delete", "db_spoof_insert", "owner_transfer", "own_update_denied"])
def test_denial_or_positive_control_failure_never_passes_and_cleans_up(failure):
    fixture = MutationFixture(failure, cap=True)
    with pytest.raises(WriteCheckFailed) as exc:
        fixture.run()
    assert "private" not in str(exc.value)
    assert "fixture-token" not in str(exc.value)
    assert fixture.rows == fixture.before


def test_api_response_timeout_still_cleans_the_marked_insert():
    fixture = MutationFixture("api_timeout")
    with pytest.raises(httpx.ReadTimeout):
        fixture.run()
    assert fixture.rows == fixture.before


def test_cleanup_failure_reports_marker_without_credentials_and_preserves_existing_rows():
    fixture = MutationFixture("api_error", cleanup_failure=True)
    with pytest.raises(WriteCheckFailed, match="cleanup incomplete") as exc:
        fixture.run()
    assert MARKER in str(exc.value)
    assert "private" not in str(exc.value)
    for table, entries in fixture.before.items():
        assert all(fixture.rows[table][key] == value for key, value in entries.items())
    assert any(row["note"] == MARKER for entries in fixture.rows.values() for row in entries.values())


def test_existing_marker_is_not_modified_or_cleaned_up():
    fixture = MutationFixture()
    next(iter(fixture.rows["income_events"].values()))["note"] = MARKER
    snapshot = copy.deepcopy(fixture.rows)
    with pytest.raises(WriteCheckFailed, match="already exists"):
        fixture.run()
    assert fixture.rows == snapshot
    assert all(request.method == "GET" for request in fixture.calls)


def test_preexisting_id_is_never_patched_or_deleted_even_if_api_reuses_it():
    fixture = MutationFixture("api_reuses_seed")
    with pytest.raises(WriteCheckFailed, match="cleanup incomplete"):
        fixture.run()
    assert all(set(entries).issubset(fixture.rows[table]) for table, entries in fixture.before.items())
    assert not any(request.method in ("PATCH", "DELETE") for request in fixture.calls)


def test_invalid_marker_makes_no_requests():
    fixture = MutationFixture()
    with httpx.Client(transport=httpx.MockTransport(fixture.handler)) as client, pytest.raises(WriteCheckFailed, match="Invalid"):
        verify_mutations(client, API, PROJECT, KEY, SESSIONS, "Existing user record", fixture.protected)
    assert fixture.calls == []
