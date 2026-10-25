# Boloka API

FastAPI service for authenticated income and expense tracking, CSV import, and transparent shortfall estimates.

## Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Set `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, and `CORS_ORIGINS` in `.env`. ES256/RS256 projects use public signing keys automatically. Only legacy HS256 projects need `SUPABASE_JWT_SECRET`. Run `../supabase/schema.sql` before using data routes. Never expose the service-role key to a client or commit `.env`.

`GET /api/v1/health` is public. Other routes require `Authorization: Bearer <Supabase access token>`. The API verifies the token subject, validates request fields, and scopes database calls to that subject. The database adapter forwards the verified caller JWT with the public project key, so RLS enforces ownership as well as API filters.

See [`../docs/api.md`](../docs/api.md), [`../docs/judge-demo.md`](../docs/judge-demo.md), and [`../supabase/schema.sql`](../supabase/schema.sql).

## Database ownership and token configuration

User-data routes require `SUPABASE_PUBLISHABLE_KEY` (a `sb_publishable_...`
key or legacy `anon` JWT). Secret/service-role keys fail closed. Remove the old
`SUPABASE_SERVICE_ROLE_KEY` setting from the API deployment; it is no longer
used. The verified caller token is forwarded on every database page and write,
including CSV imports. RLS evaluates that user's `auth.uid()`; API owner filters
remain an additional boundary.

The verifier supports ES256/RS256 through the project's HTTPS
`/auth/v1/.well-known/jwks.json` endpoint. Optional `SUPABASE_JWKS_URL` must
exactly match that endpoint. Token-provided key URLs are ignored. Public key
sets are cached for 60 seconds; newly rotated keys may take that long to appear,
and removed keys may remain accepted until the cache expires. Unknown key IDs
return 401 without forcing a refresh; unavailable/malformed key services return
503. Configure legacy HS256 explicitly with `SUPABASE_JWT_SECRET` when needed;
an `sb_secret_` API key is not a JWT signing secret and is not needed by this app.
All tokens require a valid signature, matching issuer and audience, expiry,
UUID subject and `authenticated` role. Do not disable validation or substitute
a service token.

CI starts a disposable PostgreSQL instance, bootstraps test-only auth objects,
applies the real schema, then runs `supabase/tests/rls.sql`. It checks two-user
reads, writes, ownership transfers and anonymous denial. Never run
`supabase/tests/bootstrap.sql` against hosted Supabase. A deployed two-account
test with real user JWTs remains necessary after project configuration.

References: [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security)
and [API keys](https://supabase.com/docs/guides/getting-started/api-keys).

## Forecast method and limits

The pandas baseline averages the last eight completed weeks, preserving zero
recorded-income weeks. It excludes the current partial week and future earnings.
There is no ML dependency or claim of forecast accuracy. Two completed weeks
are needed to show an income estimate; six plus an expense basis are needed
for a conditional planning gap. Confidence remains low.

Explicit future costs count once within the next 30 days. Everyday spending
uses the recent non-recurring daily mean only when records span 14 days. Past
recurring flags are not treated as due dates or automatically repeated. The
cash scenario can use an optional available balance; the ledger net is not a
bank balance. No precise shortfall date or probability is returned. See the
API contract for formulas, thresholds, limitations and exact rounding.

## Checks

From `backend/`, run `pip install pytest ruff`, `ruff check .`, and `pytest -q`.

The interactive `python -m app.release_check --api-url <API base>` checks two
dedicated seeded accounts without financial writes by default. The explicit
`--check-writes` flag adds temporary-record ownership probes and cleanup; see
the [operator runbook](../docs/judge-demo.md#opt-in-two-account-writedelete-check)
for scope, safe account selection and cleanup recovery. Mock tests are not
evidence that the deployed project passes these checks.
