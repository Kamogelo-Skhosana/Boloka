from functools import lru_cache
from urllib.parse import urlsplit
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=4)
def _jwks_client(url: str) -> jwt.PyJWKClient:
    # Do not cache individual keys beyond the set's lifetime (rotation/revocation).
    return jwt.PyJWKClient(url, lifespan=60, timeout=5)


def _verification_key(token: str) -> tuple[object, str]:
    header = jwt.get_unverified_header(token)
    algorithm = header.get("alg")
    if algorithm == "HS256" and settings.supabase_jwt_secret:
        return settings.supabase_jwt_secret, "HS256"
    if algorithm not in ("ES256", "RS256") or not isinstance(header.get("kid"), str) or not header["kid"]:
        raise jwt.InvalidTokenError("Unsupported signing algorithm or missing key id")

    project = settings.supabase_url.rstrip("/")
    expected = f"{project}/auth/v1/.well-known/jwks.json"
    parsed = urlsplit(project)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.path or parsed.query or parsed.fragment
            or settings.supabase_jwks_url not in ("", expected)):
        raise HTTPException(status_code=503, detail="Authentication signing keys are not configured")
    try:
        # Only the configured project's URL is used; token jku/x5u are ignored.
        # Unknown ids do not force network refreshes. Rotation is picked up within
        # 60 seconds, bounding repeated attacker-controlled cache misses.
        keys = _jwks_client(expected).get_signing_keys()
    except (jwt.PyJWTError, ValueError, TypeError, KeyError) as exc:
        raise HTTPException(status_code=503, detail="Authentication signing keys are unavailable") from exc
    for key in keys:
        if key.key_id == header["kid"] and key.algorithm_name == algorithm:
            return key.key, algorithm
    raise jwt.InvalidTokenError("Unknown signing key")


def get_current_user_claims(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict:
    """Verify a Supabase access token and return its trusted claims.

    Accept project ES256/RS256 signing keys, or explicitly configured legacy
    HS256. Identity always comes from verified claims, never request parameters.
    """
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "unauthenticated", "message": "A bearer token is required"}},
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not settings.supabase_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": {"code": "auth_unconfigured", "message": "Authentication is not configured"}},
        )

    try:
        key, algorithm = _verification_key(creds.credentials)
        payload = jwt.decode(
            creds.credentials,
            key,
            algorithms=[algorithm],
            audience="authenticated",
            issuer=f"{settings.supabase_url.rstrip('/')}/auth/v1",
            options={"require": ["exp", "sub", "aud", "iss"]},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "invalid_token", "message": "Invalid or expired token"}},
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        UUID(payload["sub"])
        if payload.get("role") != "authenticated":
            raise ValueError("Only authenticated user tokens are accepted")
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "invalid_token", "message": "Invalid user identity"}},
        ) from exc
    return payload


def get_current_user_id(claims: dict = Depends(get_current_user_claims)) -> str:
    return claims["sub"]


def get_current_access_token(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    _claims: dict = Depends(get_current_user_claims),
) -> str:
    """Forward only a token that passed this request's cached verification."""
    if creds is None:
        raise HTTPException(status_code=401, detail="A bearer token is required")
    return creds.credentials
