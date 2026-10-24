# Boloka API Contract

Version 1. This is the agreed interface between the frontend and the backend. Build against this; change it only by agreement (and update this file in the same PR).

## Conventions

- Base URL: `/api/v1`
- Auth: every endpoint except `/health` requires a Supabase access token in the header: `Authorization: Bearer <jwt>`. The user id is taken from the verified token, never from the request body or a URL parameter.
- All requests and responses are JSON.
- Money is stored and sent as integer cents in ZAR (`amount_cents`). Example: R150.00 is `15000`. This avoids floating-point rounding bugs.
- Dates are ISO `YYYY-MM-DD`. Timestamps are ISO 8601 UTC.
- A user can only ever read or change their own rows. Ownership is enforced in the database (RLS) as well as in the API.

## Error shape

Every error returns the same body:

    { "error": { "code": "not_found", "message": "Income entry not found" } }

Status codes: 400 bad request, 401 unauthenticated, 403 not owner, 404 not found, 422 validation error.

## Health

    GET /api/v1/health
    -> 200 { "status": "ok" }

## Account

    GET /api/v1/me
    -> 200 { "id": "uuid", "email": "user@example.com", "created_at": "..." }

Sign-up, sign-in and sign-out are handled on the client by the Supabase Auth SDK. The backend only verifies the token.

## Income

    GET /api/v1/income?from=2026-09-01&to=2026-10-31
    -> 200 { "items": [ Income, ... ] }

    POST /api/v1/income
    body: { "amount_cents": 15000, "source": "Microworkers", "received_on": "2026-10-24", "note": "batch payout" }
    -> 201 Income

    PATCH /api/v1/income/{id}
    body: any subset of { amount_cents, source, received_on, note }
    -> 200 Income

    DELETE /api/v1/income/{id}
    -> 204

    POST /api/v1/income/import   (multipart CSV: columns amount,source,received_on,note)
    -> 200 { "imported": 42, "skipped": 0 }

Income object:

    {
      "id": "uuid",
      "amount_cents": 15000,
      "source": "Microworkers",
      "received_on": "2026-10-24",
      "note": "batch payout",
      "created_at": "..."
    }

## Expenses

Same shape as income at `/api/v1/expenses`.

    POST /api/v1/expenses
    body: { "amount_cents": 90000, "category": "rent", "spent_on": "2026-10-01", "recurring": true, "note": "" }
    -> 201 Expense

Expense object adds `category` (text) and `recurring` (boolean) in place of `source`, and uses `spent_on` for the date.

## Savings contributions

Contributions record amounts the user has actually put aside. The monthly dashboard progress sums entries from the first day of the current month through today; it never treats a forecast suggestion as a saved amount.

    GET /api/v1/savings?from=2026-10-01&to=2026-10-31
    -> 200 { "items": [ { "id": "uuid", "amount_cents": 10000, "saved_on": "2026-10-24", "note": "Buffer" } ] }

    POST /api/v1/savings
    body: { "amount_cents": 10000, "saved_on": "2026-10-24", "note": "Buffer" }
    -> 201 SavingsContribution

    DELETE /api/v1/savings/{id}
    -> 204

Savings rows are owner-scoped and protected by the `savings_contributions` RLS policy in `supabase/schema.sql`. Apply the updated schema before deploying a backend that uses these endpoints.

## Forecast (the core)

    GET /api/v1/forecast
    -> 200
    {
      "generated_at": "2026-10-24T18:00:00Z",
      "horizon_days": 30,
      "predicted_income_cents": 520000,
      "predicted_expenses_cents": 610000,
      "shortfall": {
        "likely": true,
        "date": "2026-11-22",
        "amount_cents": 48000
      },
      "set_aside": {
        "weekly_cents": 15000,
        "reason": "Covers the predicted gap around the 22nd with a small buffer."
      },
      "confidence": "medium",
      "explanation": "Based on your last 8 weeks, income dips in the final third of the month while rent falls due. Setting aside R150 a week closes the gap.",
      "series": [
        { "week_start": "2026-10-27", "predicted_income_cents": 130000, "lower_cents": 90000, "upper_cents": 170000 }
      ]
    }

When there is too little history to model, the backend returns the same shape with `"confidence": "low"` and a heuristic set-aside (cold-start fallback, issue #22).

## Dashboard summary

    GET /api/v1/summary
    -> 200
    {
      "balance_cents": 240000,
      "this_week_income_cents": 130000,
      "set_aside_progress_cents": 30000,
      "set_aside_target_cents": 60000,
      "next_shortfall": { "date": "2026-11-22", "amount_cents": 48000 }
    }
