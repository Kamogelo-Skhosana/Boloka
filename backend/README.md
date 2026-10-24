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

Income is grouped into continuous weeks using pandas, including zero-income gaps. With at least twelve completed weeks, a scikit-learn Ridge trend model is fitted to the preceding weeks and compared with the recency-weighted baseline on the last four completed weeks. It is selected only when its mean absolute error is at least 10% lower; otherwise the baseline remains. A selected model is refitted on up to 52 completed weeks. Predictions are bounded between zero and twice the largest earning in the last eight training weeks.

The current partial week is excluded from training, except for a low-confidence baseline when there are no completed weeks. Known recent outflows and median observed recurring costs form the expense estimate. Confidence is low below six completed weeks and capped at medium thereafter. The four-week comparison is a model-selection check, not a population accuracy claim. Planning ranges are illustrative, not calibrated confidence intervals. Shortfall dating remains the existing heuristic pending issue #19.

The 30-day income total equals the sum of the displayed seven-day forecast blocks, with the final two-day block prorated. Expense estimates scale from the observed monthly budget to the horizon. Synthetic regression tests verify trend selection, fallback, no holdout leakage, bounds, and total consistency; opt-in real-user evaluation is still required.

References: [Ridge regression](https://scikit-learn.org/1.5/modules/generated/sklearn.linear_model.Ridge.html) and [chronological validation for time series](https://scikit-learn.org/1.5/modules/cross_validation.html#time-series-split).

## Checks

From `backend/`, run `pip install pytest ruff`, `ruff check .`, and `pytest -q`.
