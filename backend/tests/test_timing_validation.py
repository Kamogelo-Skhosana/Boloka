from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.timing_validation import TimingCase, TimingDataset, evaluate_timing, main


def case(predicted=None, cash=(100, -1, -5)):
    return {
        "cutoff_at": "2026-10-25T20:00:00+02:00",
        "prediction_recorded_at": "2026-10-25T19:00:00+02:00",
        "horizon_days": 3,
        "predicted_date": predicted,
        "complete_cash_record": True,
        "daily_cash": [{"day": f"2026-10-{26 + index}", "closing_cash_cents": amount}
                       for index, amount in enumerate(cash)],
    }


def evaluate(*rows, tolerance=0):
    return evaluate_timing(TimingDataset.model_validate({"cases": list(rows)}).cases, tolerance_days=tolerance)


def test_confusion_counts_include_abstentions_and_false_alarms():
    report = evaluate(case("2026-10-27"), case("2026-10-26", (0, 10, 20)),
                      case(), case(None, (0, 10, 20)))
    assert report["counts"] == {"true_positive": 1, "false_positive": 1, "false_negative": 1, "true_negative": 1}
    assert report["abstentions"] == 2
    assert report["warning_precision"] == report["shortfall_recall"] == report["false_alarm_rate"] == 0.5
    assert report["timely_shortfall_recall"] == 0.5
    assert report["baselines"]["always_abstain"]["missed_shortfalls"] == 2
    assert report["baselines"]["always_warn"]["false_alarms"] == 2


def test_wrong_date_is_not_counted_as_timely_even_when_event_is_detected():
    report = evaluate(case("2026-10-28"), case("2026-10-26"))
    assert report["counts"]["true_positive"] == 2
    assert report["warnings_within_tolerance"] == 0
    assert report["mean_absolute_date_error_days"] == 1
    assert report["mean_signed_date_error_days"] == 0
    assert evaluate(case("2026-10-28"), tolerance=1)["timely_shortfall_recall"] == 1


def test_missing_denominators_are_unknown_not_perfect_scores():
    report = evaluate(case(None, (0, 1, 2)))
    assert report["warning_precision"] is None
    assert report["shortfall_recall"] is None
    assert report["timely_shortfall_recall"] is None
    assert report["mean_absolute_date_error_days"] is None
    assert report["false_alarm_rate"] == 0


def test_first_negative_day_not_lowest_cash_or_first_zero_and_order_is_irrelevant():
    row = case("2026-10-27", (0, -1, -1000))
    row["daily_cash"].reverse()
    assert evaluate(row)["mean_absolute_date_error_days"] == 0


@pytest.mark.parametrize("field,value", [
    ("complete_cash_record", False), ("complete_cash_record", "true"),
    ("prediction_recorded_at", "2026-10-25T20:00:01+02:00"),
    ("prediction_recorded_at", "2026-10-25T19:00:00"),
    ("cutoff_at", "2026-10-25T20:00:00"),
    ("predicted_date", "2026-10-25"), ("predicted_date", "2026-10-29"),
    ("horizon_days", True), ("horizon_days", 0), ("horizon_days", 91),
])
def test_invalid_or_post_cutoff_candidates_are_rejected(field, value):
    row = case()
    row[field] = value
    with pytest.raises(ValidationError):
        TimingCase.model_validate(row)


@pytest.mark.parametrize("change", ["missing", "duplicate", "outside", "fractional", "boolean", "unknown"])
def test_daily_records_require_complete_unique_integer_cash(change):
    row = case()
    if change == "missing":
        row["daily_cash"].pop()
    elif change == "duplicate":
        row["daily_cash"][1] = deepcopy(row["daily_cash"][0])
    elif change == "outside":
        row["daily_cash"][0]["day"] = "2026-10-25"
    elif change == "unknown":
        row["daily_cash"][0]["email"] = "private@example.invalid"
    else:
        row["daily_cash"][0]["closing_cash_cents"] = True if change == "boolean" else 1.1
    with pytest.raises(ValidationError):
        TimingCase.model_validate(row)


def test_cutoff_uses_johannesburg_date_and_compares_timestamp_instants():
    row = case()
    row["cutoff_at"] = "2026-10-25T22:30:00Z"  # Already 26 October locally.
    row["prediction_recorded_at"] = "2026-10-26T00:00:00+02:00"
    with pytest.raises(ValidationError):  # Day 26 is not in this future horizon.
        TimingCase.model_validate(row)


@pytest.mark.parametrize("tolerance", [-1, 8, True, 1.5])
def test_invalid_date_tolerance_is_rejected(tolerance):
    with pytest.raises(ValueError):
        evaluate(case(), tolerance=tolerance)


def test_empty_dataset_is_rejected():
    with pytest.raises(ValidationError):
        TimingDataset.model_validate({"cases": []})
    with pytest.raises(ValueError):
        evaluate_timing([])


def test_cli_does_not_echo_private_invalid_inputs(tmp_path, monkeypatch, capsys):
    path = tmp_path / "private.json"
    path.write_text('{"cases": [{"password": "do-not-print-private"}]}')
    monkeypatch.setattr("sys.argv", ["timing_validation", str(path)])
    assert main() == 1
    output = capsys.readouterr().out
    assert "do-not-print-private" not in output
    assert str(path) not in output


def test_cli_outputs_only_aggregate_metrics(tmp_path, monkeypatch, capsys):
    import json

    path = tmp_path / "cases.json"
    path.write_text(json.dumps({"cases": [case("2026-10-27")]}))
    monkeypatch.setattr("sys.argv", ["timing_validation", str(path)])
    assert main() == 0
    output = capsys.readouterr().out
    assert json.loads(output)["warnings_within_tolerance"] == 1
    assert "2026-10-27" not in output
