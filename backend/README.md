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

Set `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`, and `CORS_ORIGINS` in `.env`. Run `../supabase/schema.sql` before using data routes. Never expose the service-role key to a client or commit `.env`.

`GET /api/v1/health` is public. Other routes require `Authorization: Bearer <Supabase access token>`. The API verifies the token subject, validates request fields, and scopes database calls to that subject. The database adapter uses the service-role key only on this server.

See [`../docs/api.md`](../docs/api.md), [`../docs/judge-demo.md`](../docs/judge-demo.md), and [`../supabase/schema.sql`](../supabase/schema.sql).

## Forecast method and limits

Income is grouped into weeks using pandas and a recency-weighted average. Known recent outflows and median observed recurring costs form the expense estimate. Confidence is labelled low with fewer than six observed weeks, medium from six to eleven, and high at twelve or more. This is an explainable prototype baseline, not a validated financial forecast. No Prophet or scikit-learn performance is claimed.

## Checks

From `backend/`, run `pip install pytest ruff`, `ruff check .`, and `pytest -q`.
