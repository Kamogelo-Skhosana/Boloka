from datetime import date, timedelta

import pytest

from app.forecasting import build_forecast, weekly_income


def test_weekly_income_aggregates_rows_and_ignores_future_entries():
    today = date(2026, 10, 24)
    rows = [
        {"received_on": "2026-10-19", "amount_cents": 10000},
        {"received_on": "2026-10-20", "amount_cents": 5000},
        {"received_on": "2026-10-30", "amount_cents": 90000},
    ]

    result = weekly_income(rows, today)

    assert len(result) == 1
    assert result[0]["amount_cents"] == 15000


def test_weekly_income_keeps_internal_and_trailing_zero_income_weeks():
    rows = [
        {"received_on": "2026-10-05", "amount_cents": 10000},
        {"received_on": "2026-09-21", "amount_cents": 20000},
        {"received_on": "2026-09-27", "amount_cents": 5000},
    ]
    assert weekly_income(rows, date(2026, 10, 24)) == [
        {"week_start": "2026-09-21", "amount_cents": 25000},
        {"week_start": "2026-09-28", "amount_cents": 0},
        {"week_start": "2026-10-05", "amount_cents": 10000},
        {"week_start": "2026-10-12", "amount_cents": 0},
        {"week_start": "2026-10-19", "amount_cents": 0},
    ]


@pytest.mark.parametrize("invalid", [
    {},
    {"received_on": "bad-date", "amount_cents": 1000},
    {"received_on": "2026-10-19", "amount_cents": "bad-amount"},
    {"received_on": "2026-10-19", "amount_cents": None},
    {"received_on": "2026-10-19", "amount_cents": -10},
    {"received_on": "2026-10-19", "amount_cents": 0},
    {"received_on": "2026-10-19", "amount_cents": 1.5},
    {"received_on": "2026-10-19", "amount_cents": 2_000_000_001},
    {"received_on": "2026-11-01", "amount_cents": 1000},
])
def test_weekly_income_ignores_invalid_rows_without_losing_valid_earnings(invalid):
    valid = {"received_on": "2026-10-19", "amount_cents": 5000}
    assert weekly_income([invalid, valid], date(2026, 10, 24)) == [
        {"week_start": "2026-10-19", "amount_cents": 5000},
    ]
    assert weekly_income([invalid], date(2026, 10, 24)) == []


def income_history(today, count=8, cents=70000):
    return [{"received_on": (today - timedelta(weeks=index)).isoformat(), "amount_cents": cents} for index in range(1, count + 1)]


def test_empty_history_is_not_a_reassuring_warning():
    result = build_forecast([], [], today=date(2026, 10, 24))
    assert result["shortfall"] == {"likely": False, "date": None, "amount_cents": 0, "status": "insufficient_data"}
    assert result["available_balance_cents"] is None
    assert result["set_aside"]["weekly_cents"] == 0
    assert not result["income_estimate_available"]
    assert result["series"] == []  # Unknown income must not be plotted as zero earnings.
    assert result["confidence"] == "low"


def test_explanation_exposes_exact_income_basis_and_cash_assumption():
    today = date(2026, 10, 24)
    incomes = income_history(today, cents=1)
    # Current/future payouts must not enter the explanation's income basis.
    incomes += [{"received_on": today.isoformat(), "amount_cents": 50000},
                {"received_on": "2026-11-01", "amount_cents": 90000}]
    costs = [{"spent_on": "2026-10-25", "amount_cents": 10000}]
    result = build_forecast(incomes, costs, today=today, available_balance_cents=123)
    assert result["calculation"] == {"income_history_cents": 8, "income_history_days": 56,
                                      "cash_assumed_cents": 123}
    assert result["predicted_income_cents"] == round(8 / 56 * 30)
    assert result["recommendation_reason"] == "planning_gap"
    assert result["shortfall"]["amount_cents"] == 10000 - 4 - 123


@pytest.mark.parametrize("scenario,expected", [
    ("empty", "insufficient_income_history"),
    ("no_costs", "insufficient_cost_history"),
    ("overlap", "overlapping_costs"),
    ("covered", "no_gap_in_estimate"),
])
def test_explanation_identifies_why_recommendation_is_available_or_withheld(scenario, expected):
    today = date(2026, 10, 24)
    incomes = [] if scenario == "empty" else income_history(today)
    expenses = [] if scenario in ("empty", "no_costs") else [
        {"spent_on": "2026-10-25", "amount_cents": 10000, "recurring": scenario != "overlap"},
    ]
    if scenario == "overlap":
        expenses.append({"spent_on": "2026-10-01", "amount_cents": 10000})
    result = build_forecast(incomes, expenses, today=today)
    assert result["recommendation_reason"] == expected
    assert result["calculation"]["cash_assumed_cents"] == 0
    assert result["available_balance_cents"] is None
    assert "too little history" not in result["explanation"]
    assert result["shortfall"]["date"] is None
    if scenario == "overlap":
        assert "overlap" in result["explanation"]
    if scenario == "covered":
        assert "every bill" in result["explanation"]


def test_partial_week_and_future_income_are_not_extrapolated():
    today = date(2026, 10, 24)
    rows = [{"received_on": today.isoformat(), "amount_cents": 100000}, {"received_on": "2026-11-01", "amount_cents": 100000}]
    result = build_forecast(rows, [], today=today)
    assert result["predicted_income_cents"] == 0
    assert result["history_weeks"] == 0


def test_missing_weeks_reduce_mean_and_old_earnings_do_not_expand_window():
    today = date(2026, 10, 24)
    rows = [{"received_on": "2026-10-05", "amount_cents": 21000}, {"received_on": "2000-01-01", "amount_cents": 2000000000}]
    result = build_forecast(rows, [], today=today)
    assert result["history_weeks"] == 8
    assert len(weekly_income(rows, today)) == 9
    assert result["predicted_income_cents"] == 11250


@pytest.mark.parametrize("horizon", [1, 7, 28, 30, 90])
def test_exact_horizon_totals_and_last_partial_block(horizon):
    today = date(2026, 10, 24)
    result = build_forecast(income_history(today), [], today=today, horizon_days=horizon)
    assert sum(row["predicted_income_cents"] for row in result["series"]) == result["predicted_income_cents"] == horizon * 10000
    assert sum(row["days"] for row in result["series"]) == horizon
    assert result["series"][0]["week_start"] == "2026-10-25"
    assert result["horizon_end"] == (today + timedelta(days=horizon)).isoformat()
    assert result["confidence"] == "low"


def test_expense_timing_and_same_category_bills_are_counted_once():
    today = date(2026, 10, 24)
    costs = [
        {"spent_on": "2026-10-24", "amount_cents": 1000, "recurring": True},
        {"spent_on": "2026-10-25", "amount_cents": 2000, "category": "rent", "recurring": True},
        {"spent_on": "2026-10-26", "amount_cents": 3000, "category": "rent", "recurring": True},
        {"spent_on": "2026-11-23", "amount_cents": 4000},
        {"spent_on": "2026-11-24", "amount_cents": 9000},
    ]
    result = build_forecast([], costs, today=today)
    assert result["scheduled_expenses_cents"] == result["predicted_expenses_cents"] == 9000
    assert result["shortfall"]["date"] is None
    assert result["shortfall"]["likely"] is False
    assert result["shortfall"]["status"] == "insufficient_data"


def test_known_available_cash_changes_gap_but_ledger_net_is_not_available_cash():
    today = date(2026, 10, 24)
    income = income_history(today)
    expenses = [{"spent_on": "2026-10-25", "amount_cents": 400000}]
    unknown = build_forecast(income, expenses, today=today)
    covered = build_forecast(income, expenses, today=today, available_balance_cents=100000)
    assert unknown["recorded_net_cents"] == 560000
    assert unknown["shortfall"]["amount_cents"] == 100000
    assert unknown["shortfall"]["status"] == "planning_gap"
    assert covered["shortfall"]["amount_cents"] == 0
    assert covered["shortfall"]["status"] == "no_gap_in_estimate"
    assert unknown["shortfall"]["date"] is covered["shortfall"]["date"] is None
    assert unknown["set_aside"]["total_cents"] == 100000
    assert unknown["set_aside"]["weekly_cents"] == 23334


def test_everyday_spending_requires_observation_span_and_excludes_recurring():
    today = date(2026, 10, 24)
    rows = [{"spent_on": "2026-10-11", "amount_cents": 14000}, {"spent_on": "2026-10-24", "amount_cents": 14000, "recurring": True}]
    result = build_forecast([], rows, today=today)
    assert result["everyday_estimate_available"]
    assert result["everyday_expenses_cents"] == 30000
    sparse = build_forecast([], rows[1:], today=today)
    assert not sparse["everyday_estimate_available"]
    assert sparse["everyday_expenses_cents"] == 0


@pytest.mark.parametrize("horizon", [0, -1, 91, True])
def test_invalid_horizon(horizon):
    with pytest.raises(ValueError):
        build_forecast([], [], horizon_days=horizon)


def test_fractional_daily_income_preserves_total_cents():
    today = date(2026, 10, 24)
    result = build_forecast(income_history(today, cents=1), [], today=today)
    assert result["predicted_income_cents"] == 4
    assert sum(row["predicted_income_cents"] for row in result["series"]) == 4


def test_overlapping_everyday_and_upcoming_costs_do_not_produce_a_recommendation():
    today = date(2026, 10, 24)
    expenses = [
        {"spent_on": "2026-10-01", "amount_cents": 30000, "category": "food"},
        {"spent_on": "2026-10-25", "amount_cents": 1000000, "category": "food"},
    ]
    result = build_forecast(income_history(today), expenses, today=today)
    assert result["costs_overlap_possible"]
    assert result["shortfall"]["status"] == "insufficient_data"
    assert result["shortfall"]["amount_cents"] == 0
    assert result["set_aside"]["total_cents"] == 0
