"""Small, explicit Supabase PostgREST adapter.

The API verifies the caller's JWT first, then scopes every database query to the
verified subject. The service key is only read on the server and is never sent
back to the client.
"""

from typing import Any

import httpx
from fastapi import HTTPException, status

from .config import settings


def request_table(
    method: str,
    table: str,
    *,
    user_id: str,
    params: dict[str, str] | None = None,
    payload: Any = None,
    prefer: str | None = None,
) -> Any:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": {"code": "database_unconfigured", "message": "Database is not configured"}},
        )

    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    query = {"select": "*", **(params or {})}
    # Never trust a client-supplied user_id, even though the JWT has already
    # been validated. Inserts receive their owner from the verified subject.
    if method.upper() != "POST":
        query["user_id"] = f"eq.{user_id}"
    try:
        response = httpx.request(
            method,
            f"{settings.supabase_url.rstrip('/')}/rest/v1/{table}",
            headers=headers,
            params=query,
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
    return response.json() if response.content else None

