"""Small, explicit Supabase PostgREST adapter.

The API verifies the caller's JWT and forwards it as database Authorization.
The public project key identifies the application; the caller's JWT establishes
auth.uid() and the authenticated role, so RLS enforces ownership independently
of the API filters. Privileged application keys are never used here.
"""

from typing import Any

import httpx
import jwt
from fastapi import HTTPException, status

from .config import settings


def request_table(
    method: str,
    table: str,
    *,
    user_id: str,
    access_token: str,
    params: dict[str, str] | None = None,
    payload: Any = None,
    prefer: str | None = None,
) -> Any:
    public_key = settings.supabase_publishable_key
    is_public_key = public_key.startswith("sb_publishable_")
    if public_key and not is_public_key:
        try:
            # Classify legacy API keys only. This is NOT caller authentication;
            # the Supabase gateway verifies whether the public key is valid.
            is_public_key = jwt.decode(public_key, options={"verify_signature": False}).get("role") == "anon"
        except jwt.PyJWTError:
            pass
    if not settings.supabase_url or not is_public_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": {"code": "database_unconfigured", "message": "Database is not configured"}},
        )

    if not access_token:
        raise HTTPException(status_code=401, detail="A user access token is required")
    headers = {
        "apikey": public_key,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    query = {"select": "*", **(params or {})}
    # Never trust a client-supplied user_id, even though the JWT has already
    # been validated. Inserts receive their owner from the verified subject.
    if method.upper() != "POST":
        query["user_id"] = f"eq.{user_id}"
    is_read = method.upper() == "GET"
    if is_read:
        query["order"] = query.get("order", "id.asc")
        if "id." not in query["order"]:
            query["order"] += ",id.asc"
    rows: list[dict[str, Any]] = []
    while True:
        # PostgREST may enforce a lower page size than requested. Continue until
        # empty, not until a short page, to avoid silently truncated forecasts.
        page_query = query | {"limit": "500", "offset": str(len(rows))} if is_read else query
        try:
            response = httpx.request(
                method,
                f"{settings.supabase_url.rstrip('/')}/rest/v1/{table}",
                headers=headers,
                params=page_query,
                json=payload,
                timeout=10,
            )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={"error": {"code": "database_unavailable", "message": "Could not reach the database"}},
            ) from exc
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={"error": {"code": "database_error", "message": "The database request failed"}},
            )
        result = response.json() if response.content else None
        if not is_read:
            return result
        if not isinstance(result, list):
            raise HTTPException(status_code=502, detail="Invalid database response")
        if not result:
            return rows
        rows.extend(result)
        if len(rows) >= 100_000:
            # Fail explicitly rather than returning a plausible incomplete total.
            raise HTTPException(status_code=503, detail="Too many records to load; contact the team for an export")
