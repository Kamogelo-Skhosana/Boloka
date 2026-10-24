"""Bounded weekly trend model selected against a chronological holdout."""

from dataclasses import dataclass
from statistics import mean, median

from sklearn.linear_model import Ridge


@dataclass(frozen=True)
class IncomeEstimate:
    weeks: list[int]
    method: str
    reason: str
    validation_weeks: int = 0
    model_mae_cents: float | None = None
    baseline_mae_cents: float | None = None


def weighted_income(values: list[int]) -> int:
    recent = values[-8:]
    if not recent:
        return 0
    weights = range(1, len(recent) + 1)
    average = round(sum(value * weight for value, weight in zip(recent, weights)) / sum(weights))
    return min(average, round(median(recent) * 2))


def _trend(values: list[int], count: int) -> list[int]:
    # One time-index feature keeps the fit small and deterministic. Every fit,
    # including the holdout fit, uses only the observations preceding its target.
    model = Ridge(alpha=1.0, solver="svd")
    model.fit([[index] for index in range(len(values))], values)
    prediction = model.predict([[len(values) + index] for index in range(count)])
    ceiling = max(values[-8:], default=0) * 2
    return [max(0, min(ceiling, round(float(value)))) for value in prediction]


def estimate_income(completed: list[int], count: int, *, partial: int = 0) -> IncomeEstimate:
    """Use Ridge only if it lowers four-week holdout MAE by at least 10%.

    At least eight training and four validation weeks are required. This is a
    per-user model-selection check, not evidence of accuracy on a population.
    """
    values = completed[-52:]
    baseline = [weighted_income(values) if values else partial] * count
    if len(values) < 12:
        return IncomeEstimate(baseline, "weighted_average", "insufficient_history")

    train, actual = values[:-4], values[-4:]
    candidate = _trend(train, len(actual))
    baseline_value = weighted_income(train)
    model_mae = mean(abs(observed - predicted) for observed, predicted in zip(actual, candidate))
    baseline_mae = mean(abs(observed - baseline_value) for observed in actual)
    selected = baseline_mae > 0 and model_mae <= baseline_mae * 0.9
    return IncomeEstimate(
        weeks=_trend(values, count) if selected else baseline,
        method="ridge_trend" if selected else "weighted_average",
        reason="lower_holdout_error" if selected else "baseline_retained",
        validation_weeks=4,
        model_mae_cents=model_mae,
        baseline_mae_cents=baseline_mae,
    )
