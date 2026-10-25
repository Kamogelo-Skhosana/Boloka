"""Opt-in, narrowly scoped mutation probes for dedicated synthetic accounts."""

from uuid import UUID, uuid4

import httpx

from .forecasting import local_today

RESOURCES = [("income", "income_events", "received_on"),
             ("expenses", "expenses", "spent_on"),
             ("savings", "savings_contributions", "saved_on")]


class WriteCheckFailed(Exception):
    """Safe failure text; never include credentials or raw response bodies."""


def _data(response: httpx.Response, status: int, label: str) -> object:
    if response.status_code != status:
        raise WriteCheckFailed(f"{label} failed (HTTP {response.status_code})")
    try:
        return response.json()
    except ValueError as exc:
        raise WriteCheckFailed(f"{label} returned invalid JSON") from exc


def _guard(row: object, owner: str, marker: str) -> dict:
    if not isinstance(row, dict) or row.get("user_id") != owner or row.get("note") != marker:
        raise WriteCheckFailed("Temporary record did not match its owner and QA marker")
    try:
        if not isinstance(row.get("id"), str):
            raise TypeError
        UUID(row["id"])
    except (ValueError, TypeError, KeyError) as exc:
        raise WriteCheckFailed("Temporary record did not contain a valid ID") from exc
    return row


def _owned(client: httpx.Client, url: str, headers: dict, owner: str, marker: str,
           entry_id: str, expected: dict | None = None) -> dict:
    rows = _data(client.get(url, headers=headers, params={"select": "*", "id": "eq." + entry_id}), 200, "Temporary owner read")
    if not isinstance(rows, list) or len(rows) != 1:
        raise WriteCheckFailed("Temporary owner record is missing or ambiguous")
    row = _guard(rows[0], owner, marker)
    if row["id"] != entry_id or (expected is not None and row != expected):
        raise WriteCheckFailed("An isolation probe changed the temporary owner record")
    return row


def _denied(response: httpx.Response, label: str, *, insert: bool = False) -> None:
    if not insert and response.status_code == 200 and _data(response, 200, label) == []:
        return
    if response.status_code == 403:
        body = _data(response, 403, label)
        if isinstance(body, dict) and body.get("code") == "42501":
            return
    raise WriteCheckFailed(f"{label} was not denied by ownership policy (HTTP {response.status_code})")


def _cleanup(client: httpx.Client, project: str, public_key: str,
             sessions: list[tuple[str, str]], marker: str, protected_ids: set[str]) -> bool:
    failed = False
    for owner, token in sessions:
        headers = {"apikey": public_key, "Authorization": "Bearer " + token, "Prefer": "return=representation"}
        for _, table, _ in RESOURCES:
            url = project + "/rest/v1/" + table
            try:
                # Repeat after deletion even if the database caps the response page.
                for _ in range(20):
                    rows = _data(client.get(url, headers=headers, params={"select": "*", "user_id": "eq." + owner, "note": "eq." + marker}), 200, "QA cleanup lookup")
                    if not isinstance(rows, list):
                        raise WriteCheckFailed("QA cleanup returned an invalid list")
                    if not rows:
                        break
                    for row in rows:
                        row = _guard(row, owner, marker)
                        if row["id"] in protected_ids:
                            raise WriteCheckFailed("Cleanup refuses to delete a pre-existing record")
                        filters = {"id": "eq." + row["id"], "user_id": "eq." + owner, "note": "eq." + marker}
                        response = client.delete(url, headers=headers, params=filters)
                        if response.status_code not in (200, 204):
                            raise WriteCheckFailed("QA cleanup deletion failed")
                        remaining = _data(client.get(url, headers=headers, params=filters), 200, "QA cleanup verification")
                        if remaining != []:
                            raise WriteCheckFailed("QA cleanup could not verify deletion")
                else:
                    raise WriteCheckFailed("QA cleanup exceeded its bounded lookup count")
            except (httpx.HTTPError, WriteCheckFailed):
                failed = True
    return not failed


def verify_mutations(client: httpx.Client, api_url: str, project_url: str,
                     public_key: str, sessions: list[tuple[str, str]], marker: str,
                     protected_ids: set[str] | None = None) -> None:
    """Create tiny QA rows, check both directions, then remove exact marked rows.

    Called only after the parent checker validates targets, distinct sessions
    and read isolation. No service key is used, and no seed/user row is edited.
    """
    protected_ids = protected_ids or set()
    prefix = "Boloka isolation QA "
    try:
        if not marker.startswith(prefix):
            raise ValueError
        UUID(marker[len(prefix):])
    except ValueError as exc:
        raise WriteCheckFailed("Invalid temporary QA marker") from exc
    mutations_started = False
    try:
        # A run marker must be absent for both accounts before any mutation.
        for owner, token in sessions:
            for _, table, _ in RESOURCES:
                existing = _data(client.get(project_url + "/rest/v1/" + table,
                    headers={"apikey": public_key, "Authorization": "Bearer " + token},
                    params={"select": "id", "user_id": "eq." + owner, "note": "eq." + marker}), 200, "QA marker preflight")
                if existing != []:
                    raise WriteCheckFailed("QA marker already exists; refusing mutation checks")
        mutations_started = True
        for index, (owner, token) in enumerate(sessions):
            other_owner, other_token = sessions[1 - index]
            own_api = {"Authorization": "Bearer " + token}
            foreign_api = {"Authorization": "Bearer " + other_token}
            own_db = own_api | {"apikey": public_key, "Prefer": "return=representation"}
            foreign_db = foreign_api | {"apikey": public_key, "Prefer": "return=representation"}
            for resource, table, date_field in RESOURCES:
                label = f"Account {'AB'[index]} {resource}"
                body = {"amount_cents": 1, date_field: local_today().isoformat(), "note": marker}
                # API must derive the owner, ignoring a spoofed body identifier.
                created = _data(client.post(api_url + "/" + resource, headers=own_api,
                                           json=body | {"user_id": other_owner}), 201, label + " create")
                created = _guard(created, owner, marker)
                if created.get("amount_cents") != 1:
                    raise WriteCheckFailed(label + " create returned an unexpected amount")
                entry_id = created["id"]
                if entry_id in protected_ids:
                    raise WriteCheckFailed("API create returned a pre-existing record; refusing mutation probes")
                row_url = api_url + "/" + resource + "/" + entry_id
                db_url = project_url + "/rest/v1/" + table
                filters = {"id": "eq." + entry_id}
                _owned(client, db_url, own_db, owner, marker, entry_id)
                # Positive controls prevent a blanket write outage looking like isolation.
                _data(client.patch(db_url, headers=own_db, params=filters, json={"amount_cents": 3}), 200, label + " own database update")
                snapshot = _owned(client, db_url, own_db, owner, marker, entry_id)
                if snapshot.get("amount_cents") != 3:
                    raise WriteCheckFailed(label + " own database update did not persist")
                if resource != "savings":  # Savings has no API PATCH route.
                    _data(client.patch(row_url, headers=own_api, json={"amount_cents": 4}), 200, label + " own API update")
                    snapshot = _owned(client, db_url, own_db, owner, marker, entry_id)
                    if snapshot.get("amount_cents") != 4:
                        raise WriteCheckFailed(label + " own API update did not persist")
                    response = client.patch(row_url, headers=foreign_api, json={"amount_cents": 2})
                    if response.status_code != 404:
                        raise WriteCheckFailed(label + " foreign API update was not rejected")
                    _owned(client, db_url, own_db, owner, marker, entry_id, snapshot)
                response = client.delete(row_url, headers=foreign_api)
                if response.status_code != 404:
                    raise WriteCheckFailed(label + " foreign API delete was not rejected")
                _owned(client, db_url, own_db, owner, marker, entry_id, snapshot)
                _denied(client.patch(db_url, headers=foreign_db, params=filters, json={"amount_cents": 2}), label + " foreign database update")
                _owned(client, db_url, own_db, owner, marker, entry_id, snapshot)
                _denied(client.delete(db_url, headers=foreign_db, params=filters), label + " foreign database delete")
                _owned(client, db_url, own_db, owner, marker, entry_id, snapshot)
                _denied(client.post(db_url, headers=foreign_db, json=body | {"id": str(uuid4()), "user_id": owner}), label + " spoofed database insert", insert=True)
                _denied(client.patch(db_url, headers=own_db, params=filters, json={"user_id": other_owner}), label + " ownership transfer", insert=True)
                _owned(client, db_url, own_db, owner, marker, entry_id, snapshot)
                if client.delete(row_url, headers=own_api).status_code != 204:
                    raise WriteCheckFailed(label + " own API delete failed")
                if _data(client.get(db_url, headers=own_db, params=filters), 200, label + " delete verification") != []:
                    raise WriteCheckFailed(label + " own API delete did not persist")
    finally:
        if mutations_started and not _cleanup(client, project_url, public_key, sessions, marker, protected_ids):
            raise WriteCheckFailed("Temporary QA cleanup incomplete; inspect only records with note: " + marker)
