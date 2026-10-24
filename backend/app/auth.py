import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

bearer = HTTPBearer(auto_error=False)


def get_current_user_claims(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),  # noqa: B008 - FastAPI dependency declaration
) -> dict:
    """Verify a Supabase access token and return its trusted claims.

    Supabase signs access tokens with HS256 using the project JWT secret and sets
    the audience to "authenticated". The user id is read from the verified token,
    never from the request body or a URL parameter.
    """
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "unauthenticated", "message": "A bearer token is required"}},
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not settings.supabase_jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": {"code": "auth_unconfigured", "message": "Authentication is not configured"}},
        )

    try:
        payload = jwt.decode(
            creds.credentials,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "invalid_token", "message": "Invalid or expired token"}},
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "invalid_token", "message": "Token is missing a subject"}},
        )
    return payload


def get_current_user_id(claims: dict = Depends(get_current_user_claims)) -> str:  # noqa: B008 - FastAPI dependency declaration
    return claims["sub"]
