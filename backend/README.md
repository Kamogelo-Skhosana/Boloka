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

Set `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_JWT_SECRET`, and `CORS_ORIGINS` in `.env`. Run `../supabase/schema.sql` before using data routes. Never expose the service-role key to a client or commit `.env`.

`GET /api/v1/health` is public. Other routes require `Authorization: Bearer <Supabase access token>`. The API verifies the token subject, validates request fields, and scopes database calls to that subject. The database adapter forwards the verified caller JWT with the public project key, so RLS enforces ownership as well as API filters.

See [`../docs/api.md`](../docs/api.md), [`../docs/judge-demo.md`](../docs/judge-demo.md), and [`../supabase/schema.sql`](../supabase/schema.sql).

## Database ownership and token configuration

User-data routes require `SUPABASE_PUBLISHABLE_KEY` (a `sb_publishable_...`
key or legacy `anon` JWT). Secret/service-role keys fail closed. Remove the old
`SUPABASE_SERVICE_ROLE_KEY` setting from the API deployment; it is no longer
used. The verified caller token is forwarded on every database page and write,
including CSV imports. RLS evaluates that user's `auth.uid()`; API owner filters
remain an additional boundary.

The current verifier supports legacy HS256 projects only. Configure the matching
project URL and JWT secret. Tokens must have a valid signature, matching issuer
and audience, expiry, UUID subject and `authenticated` role. Asymmetric signing
keys require a separately tested JWKS verifier; do not disable validation or
reuse a service token to work around an incompatible project.

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
