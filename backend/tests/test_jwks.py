import io
import json
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from fastapi.testclient import TestClient

from app import auth, database
from app.config import settings
from app.main import app

PROJECT = "https://project.example.invalid"
USER = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setattr(settings, "supabase_url", PROJECT)
    monkeypatch.setattr(settings, "supabase_jwks_url", PROJECT + "/auth/v1/.well-known/jwks.json")
    monkeypatch.setattr(settings, "supabase_jwt_secret", "")
    monkeypatch.setattr(settings, "supabase_publishable_key", "sb_publishable_test")
    auth._jwks_client.cache_clear()
    monkeypatch.setattr(database.httpx, "request", lambda *a, **kw: pytest.fail("Unexpected database call"))
    yield TestClient(app)
    auth._jwks_client.cache_clear()


def signing_key(algorithm="ES256", kid="current"):
    if algorithm == "ES256":
        private = ec.generate_private_key(ec.SECP256R1())
        public = jwt.algorithms.ECAlgorithm.to_jwk(private.public_key(), as_dict=True)
        # PyJWT 2.9's exporter drops leading zero bytes. RFC 7518 requires
        # fixed-width P-256 coordinates; otherwise random fixtures can fail.
        numbers = private.public_key().public_numbers()
        public.update({axis: jwt.utils.base64url_encode(value.to_bytes(32, "big")).decode()
                       for axis, value in (("x", numbers.x), ("y", numbers.y))})
    else:
        private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public = jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key(), as_dict=True)
    return private, {**public, "kid": kid, "alg": algorithm, "use": "sig"}


def access_token(private, algorithm="ES256", kid="current", **changes):
    claims = {"sub": USER, "role": "authenticated", "aud": "authenticated",
              "iss": PROJECT + "/auth/v1", "exp": datetime.now(UTC) + timedelta(minutes=5)}
    claims.update(changes)
    return jwt.encode(claims, private, algorithm=algorithm, headers={"kid": kid, "jku": "https://untrusted.invalid"})


def mock_keys(monkeypatch, document):
    calls = []

    def open_url(request, **kwargs):
        calls.append(request.full_url)
        return io.BytesIO(json.dumps(document).encode())

    monkeypatch.setattr("urllib.request.urlopen", open_url)
    return calls


@pytest.mark.parametrize("algorithm", ["ES256", "RS256"])
def test_verifies_asymmetric_tokens_and_forwards_caller(configured, monkeypatch, algorithm):
    import httpx

    private, public = signing_key(algorithm)
    calls = mock_keys(monkeypatch, {"keys": [public]})
    database_calls = []

    def request(*args, **kwargs):
        database_calls.append(kwargs)
        return httpx.Response(200, json=[])

    monkeypatch.setattr(database.httpx, "request", request)
    token = access_token(private, algorithm)
    for _ in range(2):
        assert configured.get("/api/v1/income", headers={"Authorization": "Bearer " + token}).status_code == 200
    assert calls == [settings.supabase_jwks_url]
    assert all(c["headers"]["Authorization"] == "Bearer " + token for c in database_calls)


@pytest.mark.parametrize("changes", [
    {"iss": "https://another.invalid/auth/v1"}, {"aud": "other"},
    {"exp": 0}, {"role": "service_role"}, {"sub": "invalid"},
])
def test_rejects_invalid_claims(configured, monkeypatch, changes):
    private, public = signing_key()
    mock_keys(monkeypatch, {"keys": [public]})
    token = access_token(private, **changes)
    assert configured.get("/api/v1/income", headers={"Authorization": "Bearer " + token}).status_code == 401


def test_wrong_signature_missing_and_unknown_key_ids(configured, monkeypatch):
    private, public = signing_key()
    other, _ = signing_key()
    calls = mock_keys(monkeypatch, {"keys": [public]})
    for token in [access_token(other), access_token(private, kid=""),
                  access_token(private, kid="unknown"), access_token(private, kid="another")]:
        assert configured.get("/api/v1/income", headers={"Authorization": "Bearer " + token}).status_code == 401
    assert len(calls) == 1


def test_rotated_key_is_loaded_after_set_expires(configured, monkeypatch):
    private, public = signing_key()
    document = {"keys": [public]}
    calls = mock_keys(monkeypatch, document)
    client = auth._jwks_client(settings.supabase_jwks_url)
    client.get_signing_keys()
    rotated, rotated_public = signing_key(kid="rotated")
    document["keys"] = [rotated_public]
    client.jwk_set_cache.jwk_set_with_timestamp.timestamp -= 61
    claims = auth.get_current_user_claims(auth.HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=access_token(rotated, kid="rotated")))
    assert claims["sub"] == USER
    assert len(calls) == 2
    with pytest.raises(jwt.InvalidTokenError):
        auth._verification_key(access_token(private))


@pytest.mark.parametrize("document", [{}, {"keys": []}, {"keys": "invalid"}])
def test_invalid_key_service_fails_closed(configured, monkeypatch, document):
    private, _ = signing_key()
    mock_keys(monkeypatch, document)
    assert configured.get("/api/v1/income", headers={"Authorization": "Bearer " + access_token(private)}).status_code == 503


def test_key_service_outage(configured, monkeypatch):
    from urllib.error import URLError

    def unavailable(*args, **kwargs):
        raise URLError("offline")

    monkeypatch.setattr("urllib.request.urlopen", unavailable)
    private, _ = signing_key()
    assert configured.get("/api/v1/income", headers={"Authorization": "Bearer " + access_token(private)}).status_code == 503


def test_untrusted_config_and_symmetric_confusion(configured, monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: pytest.fail("Untrusted URL requested"))
    private, _ = signing_key()
    monkeypatch.setattr(settings, "supabase_jwks_url", "https://another.invalid/keys")
    assert configured.get("/api/v1/income", headers={"Authorization": "Bearer " + access_token(private)}).status_code == 503
    token = jwt.encode({"sub": USER}, "attacker-key", algorithm="HS256")
    assert configured.get("/api/v1/income", headers={"Authorization": "Bearer " + token}).status_code == 401
