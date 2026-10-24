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


def test_cold_start_returns_low_confidence_and_explains_data_limit():
    result = build_forecast([], [], today=date(2026, 10, 24))

    assert result["confidence"] == "low"
    assert result["shortfall"]["likely"] is False
    assert "fewer than six weeks" in result["explanation"]
    assert len(result["series"]) == 5


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


def test_current_partial_week_does_not_change_completed_week_baseline():
    today = date(2026, 10, 24)
    history = [{"received_on": "2026-10-12", "amount_cents": 20000}]
    baseline = build_forecast(history, [], today=today)
    with_partial_week = build_forecast(history + [
        {"received_on": "2026-10-19", "amount_cents": 1000},
    ], [], today=today)
    assert baseline["predicted_income_cents"] == 85714
    assert with_partial_week["predicted_income_cents"] == baseline["predicted_income_cents"]


def test_unpaid_completed_weeks_reduce_forecast():
    result = build_forecast([
        {"received_on": "2026-09-28", "amount_cents": 20000},
    ], [], today=date(2026, 10, 24))
    # Two completed zero-income weeks must not disappear from the average.
    assert result["predicted_income_cents"] == 0
    assert result["confidence"] == "low"


def test_current_week_only_uses_low_confidence_fallback():
    result = build_forecast([
        {"received_on": "2026-10-24", "amount_cents": 10000},
    ], [], today=date(2026, 10, 24))
    assert result["confidence"] == "low"
    assert result["predicted_income_cents"] == 42857


def test_known_recurring_cost_is_not_multiplied_by_observation_count():
    today = date(2026, 10, 24)
    expenses = [
        {"amount_cents": 120000, "spent_on": "2026-09-01", "recurring": True, "category": "rent"},
        {"amount_cents": 120000, "spent_on": "2026-10-01", "recurring": True, "category": "rent"},
        {"amount_cents": 9900, "spent_on": "2026-09-20", "recurring": True, "category": "data"},
        {"amount_cents": 9900, "spent_on": "2026-10-20", "recurring": True, "category": "data"},
    ]

    result = build_forecast([], expenses, today=today)

    assert result["predicted_expenses_cents"] == 129900
    assert result["shortfall"]["likely"] is True
    assert result["set_aside"]["weekly_cents"] > 0


def test_recent_weighted_income_has_medium_confidence_with_six_weeks():
    today = date(2026, 10, 24)
    incomes = [
        {"received_on": (today - timedelta(days=7 * offset)).isoformat(), "amount_cents": 20000}
        for offset in range(1, 7)
    ]

    result = build_forecast(incomes, [], today=today)

    assert result["confidence"] == "medium"
    assert result["predicted_income_cents"] > 0
    assert "6 completed weeks" in result["explanation"]


@pytest.mark.parametrize("horizon", [1, 7, 14, 28, 30, 90])
def test_forecast_total_matches_series_and_prorates_partial_week(horizon):
    result = build_forecast([
        {"received_on": "2026-10-12", "amount_cents": 70000},
    ], [], today=date(2026, 10, 24), horizon_days=horizon)
    assert result["predicted_income_cents"] == sum(week["predicted_income_cents"] for week in result["series"])
    assert result["predicted_income_cents"] == horizon * 10000
    assert len(result["series"]) == (horizon + 6) // 7
    assert all(0 <= week["lower_cents"] <= week["predicted_income_cents"] <= week["upper_cents"] for week in result["series"])


def test_learned_model_drives_forecast_and_shortfall():
    today = date(2026, 10, 19)
    incomes = [
        {"received_on": (today - timedelta(weeks=16 - index)).isoformat(), "amount_cents": 10000 + index * 1000}
        for index in range(16)
    ]
    expenses = [{"spent_on": "2026-10-18", "amount_cents": 200000}]
    result = build_forecast(incomes, expenses, today=today)
    assert result["model"]["method"] == "ridge_trend"
    assert result["shortfall"]["likely"] is True
    assert result["shortfall"]["amount_cents"] == 200000 - result["predicted_income_cents"]
    assert "lower error" in result["explanation"]
    assert result["confidence"] == "medium"

    future = {"received_on": "2026-10-30", "amount_cents": 100000000}
    future_result = build_forecast(incomes + [future], expenses, today=today)
    for field in ["model", "series", "predicted_income_cents", "shortfall"]:
        assert future_result[field] == result[field]


@pytest.mark.parametrize("horizon", [0, -1, 91])
def test_forecast_rejects_unsupported_horizon(horizon):
    with pytest.raises(ValueError, match="horizon_days"):
        build_forecast([], [], horizon_days=horizon)


def test_expense_budget_scales_to_forecast_horizon():
    result = build_forecast([], [
        {"spent_on": "2026-10-20", "amount_cents": 30000},
    ], today=date(2026, 10, 24), horizon_days=7)
    assert result["predicted_expenses_cents"] == 7000
    assert result["shortfall"]["amount_cents"] == 7000
