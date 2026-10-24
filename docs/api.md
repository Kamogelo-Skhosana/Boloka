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

PATCH accepts omitted fields unchanged. Required fields (`amount_cents`,
`received_on`, and expense `spent_on`/`recurring`) reject explicit `null` with
422. Optional text fields can be cleared with `null`. An empty PATCH returns 400.
List date bounds are inclusive; a `from` date after `to` returns 422.

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

    GET /api/v1/forecast\n    POST /api/v1/forecast/scenario\n    body: { "available_balance_cents": 10000 }

The nonnegative available-cash scenario body is a scenario value, not stored
or bank verified. Without it, available cash is unknown. Recorded net income
is never silently substituted for available cash. The endpoint covers tomorrow
through today + 30 days, using the Africa/Johannesburg calendar.

The response retains the income/expense totals, `series`, `shortfall`, and
`set_aside` fields. It adds explicit assumptions and data availability:

- `model.method`: `pandas_weekly_mean`; no fitted ML model is used.
- `history_weeks`: up to eight completed weeks, including zero-income gaps.
- `income_estimate_available`: at least two completed weeks; otherwise the
  income total is zero as a placeholder, not a prediction of no earnings.
- `scheduled_expenses_cents`: explicitly dated costs after today and within
  the horizon, counted once each, even when categories match.
- `everyday_expenses_cents`: historical non-recurring daily mean multiplied by
  30, only when recent records span at least 14 calendar days. Recurring flags
  do not establish bill identity, cadence or due dates, so past recurring costs
  need an explicit future entry. Missing bills remain unknown.
- `available_balance_cents`: null when unknown; `recorded_net_cents` is a
  separate, incomplete ledger total. Savings contributions are transfers and
  do not automatically increase available cash or reduce the planning gap.
- `shortfall.status`: `insufficient_data`, `planning_gap` or `no_gap_in_estimate`.
  A planning gap requires six completed income weeks and an expense basis.
  It equals max(0, estimated costs - estimated earnings - scenario cash).
- `shortfall.likely` is always false and `shortfall.date` is always null: weekly
  data cannot support a payout date or calibrated risk probability. UI code
  must use status and show assumptions rather than the legacy likely flag.
- `set_aside.total_cents` is the conditional planning gap, or zero for
  insufficient inputs; weekly cents are ceil(total * 7 / 30). This is a
  scenario allocation, not proof that money can be saved.
- `confidence` remains low until evidence supports calibrated confidence.

The mean assumes records are complete during the observation window; missing
weeks are zero recorded income, not proof of no work. The current partial week
and future earnings are excluded. Older income does not extend the bounded
window. Each series row has a start date and number of days; cumulative integer
rounding ensures blocks sum exactly to the 30-day income total. No statistical
confidence band is returned. When income history is insufficient, the series
is empty rather than plotting unknown earnings as zero.

## Dashboard summary

    GET /api/v1/summary
    -> 200
    {
      "balance_cents": 240000,
      "this_week_income_cents": 130000,
      "set_aside_progress_cents": 30000,
      "set_aside_target_cents": 60000,
      "next_shortfall": null
    }

The summary balance is recorded net income less paid expenses, not available cash. `next_shortfall` remains null because no precise day/risk is established. Savings progress is the recorded current-month contribution sum, separate from the conditional horizon target; the UI does not present these as progress against a dated goal. Database reads paginate rather than silently truncating to one server page.
