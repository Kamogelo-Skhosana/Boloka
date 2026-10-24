from datetime import date, timedelta

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
        for offset in range(6)
    ]

    result = build_forecast(incomes, [], today=today)

    assert result["confidence"] == "medium"
    assert result["predicted_income_cents"] > 0
    assert "6 weeks" in result["explanation"]
