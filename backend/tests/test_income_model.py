import pytest

from app.income_model import estimate_income


@pytest.mark.parametrize("history", [[], [10000], [10000] * 11])
def test_sparse_history_keeps_baseline(history):
    result = estimate_income(history, 5, partial=5000)
    assert result.method == "weighted_average"
    assert result.reason == "insufficient_history"
    assert result.validation_weeks == 0
    assert result.weeks == [10000 if history else 5000] * 5


def test_learned_trend_selected_when_it_improves_unseen_weeks():
    result = estimate_income([10000 + index * 1000 for index in range(16)], 5)
    assert result.method == "ridge_trend"
    assert result.model_mae_cents < result.baseline_mae_cents * 0.9
    assert result.validation_weeks == 4
    assert 25000 < result.weeks[0] < 27000
    assert result.weeks == sorted(result.weeks)


def test_no_improvement_retains_constant_baseline():
    result = estimate_income([10000] * 16, 5)
    assert result.method == "weighted_average"
    assert result.reason == "baseline_retained"
    assert result.weeks == [10000] * 5
    assert result.model_mae_cents == result.baseline_mae_cents == 0


def test_validation_does_not_train_on_the_held_out_weeks():
    result = estimate_income([10000] * 8 + [0] * 4, 5)
    # The eight training weeks predict 10,000. The later zeros must remain
    # unseen until scoring, so both validation errors are exactly 10,000.
    assert result.model_mae_cents == result.baseline_mae_cents == 10000
    assert result.method == "weighted_average"


@pytest.mark.parametrize("values", [
    [100000 - index * 5000 for index in range(16)],
    [0, 0, 100000, 0] * 4,
    [0] * 16,
    [2_000_000_000] * 16,
])
def test_predictions_are_bounded_nonnegative_integer_cents(values):
    result = estimate_income(values, 13)
    assert len(result.weeks) == 13
    assert all(type(value) is int and 0 <= value <= 2 * max(values[-8:]) for value in result.weeks)


def test_model_uses_bounded_recent_training_window():
    recent = [10000 + index * 1000 for index in range(52)]
    assert estimate_income([2_000_000_000] * 100 + recent, 5) == estimate_income(recent, 5)
