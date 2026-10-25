"""Interactive, financial-record read-only checks against two seeded accounts."""

import argparse
import getpass
import sys
from dataclasses import dataclass, field
from urllib.parse import urlsplit
from uuid import UUID

import httpx
import jwt
from pydantic import ValidationError

from .config import settings
from .forecast_schema import ForecastResponse


class CheckFailed(Exception):
    """Safe diagnostic without response bodies, passwords or tokens."""


@dataclass(repr=False)
class Credentials:
    email: str = field(repr=False)
    password: str = field(repr=False)


def validate_targets(api_url: str, project_url: str, public_key: str) -> None:
    for url, project in [(api_url, False), (project_url, True)]:
        parsed = urlsplit(url)
        local = parsed.hostname in ("localhost", "127.0.0.1", "::1")
        if (not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment
                or (parsed.scheme != "https" and not (not project and local and parsed.scheme == "http"))
                or (project and parsed.path not in ("", "/"))):
            raise CheckFailed("Use HTTPS targets (HTTP allowed only for the local API), without URL credentials or query strings")
    is_public = public_key.startswith("sb_publishable_")
    if not is_public:
        try:
            is_public = jwt.decode(public_key, options={"verify_signature": False}).get("role") == "anon"
        except jwt.PyJWTError:
            pass
    if not is_public:
        raise CheckFailed("A public publishable/anon project key is required; privileged keys are rejected")


def _json(response: httpx.Response, label: str) -> object:
    if response.status_code != 200:
        raise CheckFailed(f"{label} failed (HTTP {response.status_code})")
    try:
        return response.json()
    except ValueError as exc:
        raise CheckFailed(f"{label} returned invalid JSON") from exc


def verify_accounts(client: httpx.Client, api_url: str, project_url: str,
                    public_key: str, accounts: list[Credentials]) -> dict[str, dict[str, int]]:
    validate_targets(api_url, project_url, public_key)
    if len(accounts) != 2:
        raise CheckFailed("Two distinct seeded demo accounts are required")
    api_url, project_url = api_url.rstrip("/"), project_url.rstrip("/")
    sessions: list[tuple[str, str]] = []
    results: dict[str, dict[str, int]] = {}
    try:
        for index, account in enumerate(accounts):
            label = "AB"[index]
            payload = _json(client.post(project_url + "/auth/v1/token", params={"grant_type": "password"},
                                       headers={"apikey": public_key},
                                       json={"email": account.email, "password": account.password}), f"Account {label} sign-in")
            try:
                token = payload["access_token"]
                owner = str(UUID(payload["user"]["id"]))
                if not isinstance(token, str) or not token:
                    raise ValueError
            except (TypeError, ValueError, KeyError) as exc:
                raise CheckFailed("Auth response did not contain a valid user session") from exc
            sessions.append((owner, token))
        if sessions[0][0] == sessions[1][0]:
            raise CheckFailed("The two sign-ins resolve to the same account")
        for index, (owner, token) in enumerate(sessions):
            label = "AB"[index]
            headers = {"Authorization": "Bearer " + token}
            results[label] = {}
            for resource, table in [("income", "income_events"), ("expenses", "expenses"), ("savings", "savings_contributions")]:
                body = _json(client.get(api_url + "/" + resource, headers=headers), f"Account {label} {resource}")
                if not isinstance(body, dict) or not isinstance(body.get("items"), list):
                    raise CheckFailed(f"Account {label} {resource} returned an invalid list")
                rows = body["items"]
                if any(not isinstance(row, dict) or row.get("user_id") != owner for row in rows):
                    raise CheckFailed(f"Account {label} {resource} exposed an unexpected owner")
                if resource != "savings" and not rows:
                    raise CheckFailed(f"Account {label} needs seeded income and expenses to make ownership checks meaningful")
                results[label][resource] = len(rows)
                foreign = _json(client.get(project_url + "/rest/v1/" + table,
                                          headers=headers | {"apikey": public_key},
                                          params={"select": "id", "user_id": "eq." + sessions[1 - index][0], "limit": "1"}),
                                f"Account {label} foreign {resource} probe")
                if foreign != []:
                    raise CheckFailed(f"Account {label} foreign {resource} read was not denied")
            for resource in ["forecast", "summary"]:
                body = _json(client.get(api_url + "/" + resource, headers=headers), f"Account {label} {resource}")
                if not isinstance(body, dict) or "error" in body:
                    raise CheckFailed(f"Account {label} {resource} returned an invalid result")
                if resource == "forecast":
                    try:
                        ForecastResponse.model_validate(body)
                    except ValidationError as exc:
                        raise CheckFailed(f"Account {label} forecast did not match the API contract") from exc
                elif type(body.get("balance_cents")) is not int:
                    raise CheckFailed(f"Account {label} summary did not contain a recorded balance")
    finally:
        cleanup_failed = False
        for _, token in sessions:
            try:
                response = client.post(project_url + "/auth/v1/logout", params={"scope": "local"},
                                       headers={"apikey": public_key, "Authorization": "Bearer " + token})
                cleanup_failed |= response.status_code != 204
            except httpx.HTTPError:
                cleanup_failed = True
        if cleanup_failed and sys.exc_info()[0] is None:
            raise CheckFailed("Checks finished but a temporary QA session could not be signed out")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default="http://localhost:8000/api/v1")
    args = parser.parse_args()
    try:
        validate_targets(args.api_url, settings.supabase_url, settings.supabase_publishable_key)
        if not sys.stdin.isatty():
            raise CheckFailed("Run in an interactive terminal; credentials are not accepted through command arguments or piped input")
        print("API target:", args.api_url)
        print("Auth target:", settings.supabase_url)
        print("Use two dedicated, seeded demo accounts. No financial records will be changed.")
        accounts = [Credentials(input(f"Account {label} email: ").strip(), getpass.getpass(f"Account {label} password: "))
                    for label in "AB"]
        with httpx.Client(timeout=15, follow_redirects=False) as client:
            counts = verify_accounts(client, args.api_url, settings.supabase_url, settings.supabase_publishable_key, accounts)
        print("Read checks passed; loaded record counts by account alias:", counts)
        print("NOT VERIFIED: write/delete isolation, persistence after re-login, browser redirects/CORS, device acceptance.")
        return 0
    except CheckFailed as exc:
        print("CHECK FAILED:", str(exc), file=sys.stderr)
    except httpx.HTTPError:
        print("CHECK FAILED: network request failed; check the API and Supabase connection", file=sys.stderr)
    except (EOFError, KeyboardInterrupt):
        print("Check cancelled", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
