"""Offline evaluation of pre-recorded date candidates; never a date predictor."""

import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)


class DailyCash(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: date
    closing_cash_cents: int = Field(strict=True)


class TimingCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cutoff_at: datetime
    prediction_recorded_at: datetime
    horizon_days: int = Field(strict=True, ge=1, le=90)
    predicted_date: date | None
    complete_cash_record: bool = Field(strict=True)
    daily_cash: list[DailyCash] = Field(min_length=1, max_length=90)

    @field_validator("cutoff_at", "prediction_recorded_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.utcoffset() is None:
            raise ValueError("Timestamps must include a timezone")
        return value

    @model_validator(mode="after")
    def check_window(self) -> "TimingCase":
        if not self.complete_cash_record:
            raise ValueError("Incomplete cash records cannot establish a shortfall outcome")
        if self.prediction_recorded_at > self.cutoff_at:
            raise ValueError("Prediction must be recorded at or before the cutoff")
        start = self.cutoff_at.astimezone(ZoneInfo("Africa/Johannesburg")).date()
        expected = [start + timedelta(days=offset) for offset in range(1, self.horizon_days + 1)]
        if sorted(row.day for row in self.daily_cash) != expected:
            raise ValueError("Exactly one cash observation per horizon day is required")
        if self.predicted_date is not None and self.predicted_date not in expected:
            raise ValueError("Predicted date must be inside the future horizon")
        return self


class TimingDataset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cases: list[TimingCase] = Field(min_length=1, max_length=10_000)


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def evaluate_timing(cases: list[TimingCase], *, tolerance_days: int = 0) -> dict:
    """Score first negative end-of-day cash, including abstentions and false alarms.

    This cannot verify the provenance/completeness of operator-supplied records
    or prove the candidate model used only information available at its cutoff.
    """
    if not cases:
        raise ValueError("At least one complete timing case is required")
    if type(tolerance_days) is not int or not 0 <= tolerance_days <= 7:
        raise ValueError("Date tolerance must be an integer from zero to seven days")
    counts = {"true_positive": 0, "false_positive": 0, "false_negative": 0, "true_negative": 0}
    errors = []
    abstentions = 0
    for case in cases:
        actual = next((row.day for row in sorted(case.daily_cash, key=lambda row: row.day)
                       if row.closing_cash_cents < 0), None)
        predicted = case.predicted_date
        abstentions += predicted is None
        if predicted is None:
            counts["false_negative" if actual is not None else "true_negative"] += 1
        elif actual is None:
            counts["false_positive"] += 1
        else:
            counts["true_positive"] += 1
            errors.append((predicted - actual).days)
    tp, fp, fn, tn = (counts[key] for key in ("true_positive", "false_positive", "false_negative", "true_negative"))
    within = sum(abs(error) <= tolerance_days for error in errors)
    return {
        "definition": "first_negative_end_of_day_cash",
        "cases": len(cases),
        "abstentions": abstentions,
        "counts": counts,
        "warning_precision": _ratio(tp, tp + fp),
        "shortfall_recall": _ratio(tp, tp + fn),
        "false_alarm_rate": _ratio(fp, fp + tn),
        "date_pairs": len(errors),
        "mean_absolute_date_error_days": _ratio(sum(abs(error) for error in errors), len(errors)),
        "mean_signed_date_error_days": _ratio(sum(errors), len(errors)),
        "date_tolerance_days": tolerance_days,
        "warnings_within_tolerance": within,
        "timely_shortfall_recall": _ratio(within, tp + fn),
        "baselines": {
            "always_abstain": {"missed_shortfalls": tp + fn, "false_alarms": 0},
            "always_warn": {"missed_shortfalls": 0, "false_alarms": fp + tn},
        },
        "limitations": [
            "End-of-day cash does not measure intraday missed payments or prove affordability.",
            "Completeness and pre-cutoff prediction provenance require external verification.",
            "Cases are not independent people; these descriptive results do not validate a probability or release readiness.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Private local JSON; never commit real financial records")
    parser.add_argument("--tolerance-days", type=int, default=0)
    args = parser.parse_args()
    try:
        with args.dataset.open("rb") as source:
            raw = source.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("Dataset exceeds the 2 MB limit")
        dataset = TimingDataset.model_validate_json(raw)
        report = evaluate_timing(dataset.cases, tolerance_days=args.tolerance_days)
    except (OSError, ValueError, ValidationError):
        # Validation exceptions may contain private input values: never print them.
        print("Evaluation failed: use a readable JSON file under 2 MB, complete daily cash records, timezone-aware cutoffs and predictions recorded before the cutoff. Tolerance must be 0–7 days.")
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
