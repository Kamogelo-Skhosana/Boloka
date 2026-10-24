"""Transparent pandas cash-planning baseline; no calibrated risk prediction."""

from collections.abc import Iterable
from datetime import UTC, date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


def local_today() -> date:
    return datetime.now(ZoneInfo("Africa/Johannesburg")).date()


def weekly_income(events: Iterable[dict[str, Any]], today: date) -> list[dict[str, Any]]:
    """Aggregate Monday-start weeks, filling gaps through the current week.

    The first valid earning establishes the observation window. Earlier weeks
    are unknown rather than zero. Invalid and future entries are ignored.
    """
    rows = [
        {"date": event.get("received_on"), "amount_cents": event.get("amount_cents")}
        for event in events
    ]
    if not rows:
        return []
    frame = pd.DataFrame(rows)
    frame["date"] = pd.to_datetime(frame["date"], format="%Y-%m-%d", errors="coerce")
    frame["amount_cents"] = pd.to_numeric(frame["amount_cents"], errors="coerce")
    frame = frame.dropna(subset=["date", "amount_cents"])
    frame = frame[
        frame["amount_cents"].between(1, 2_000_000_000)
        & (frame["amount_cents"] % 1 == 0)
    ]
    frame = frame[frame["date"].dt.date <= today]
    if frame.empty:
        return []
    frame["amount_cents"] = frame["amount_cents"].astype("int64")
    frame["week_start"] = frame["date"].dt.to_period("W-SUN").dt.start_time
    grouped = frame.groupby("week_start")["amount_cents"].sum()
    current_week = today - timedelta(days=today.weekday())
    weeks = pd.date_range(max(grouped.index.min(), pd.Timestamp(current_week - timedelta(weeks=8))), current_week, freq="W-MON")
    grouped = grouped.reindex(weeks, fill_value=0)
    return [
        {"week_start": week.date().isoformat(), "amount_cents": int(amount)}
        for week, amount in grouped.items()
    ]


def _valid_rows(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    valid = []
    for row in rows:
        try:
            day = date.fromisoformat(str(row.get(field, "")))
            amount = row.get("amount_cents")
            if type(amount) is not int or not 0 < amount <= 2_000_000_000:
                continue
            valid.append({**row, "day": day})
        except (ValueError, TypeError):
            continue
    return valid


def build_forecast(
    incomes: list[dict[str, Any]],
    expenses: list[dict[str, Any]],
    *,
    today: date | None = None,
    horizon_days: int = 30,
    available_balance_cents: int | None = None,
) -> dict[str, Any]:
    today = today or local_today()
    if type(horizon_days) is not int or not 1 <= horizon_days <= 90:
        raise ValueError("horizon_days must be between 1 and 90")
    if available_balance_cents is not None and (type(available_balance_cents) is not int or available_balance_cents < 0):
        raise ValueError("available_balance_cents must be a nonnegative integer or None")
    weekly = weekly_income(incomes, today)
    current_week = (today - timedelta(days=today.weekday())).isoformat()
    completed = [row for row in weekly if row["week_start"] < current_week][-8:]
    weeks = len(completed)
    income_known = weeks >= 2
    daily_income = sum(row["amount_cents"] for row in completed) / (weeks * 7) if income_known else 0
    end = today + timedelta(days=horizon_days)
    expense_rows = _valid_rows(expenses, "spent_on")
    historic = [row for row in expense_rows if today - timedelta(days=29) <= row["day"] <= today]
    # Recurring is only a flag: there is no bill identity, cadence or due date.
    # Do not invent repeats or collapse separate bills with the same category.
    everyday = [row for row in historic if not row.get("recurring")]
    observed_days = (today - min(row["day"] for row in historic)).days + 1 if historic else 0
    spending_known = observed_days >= 14
    daily_spending = sum(row["amount_cents"] for row in everyday) / observed_days if spending_known else 0
    scheduled = [row for row in expense_rows if today < row["day"] <= end]
    scheduled_cents = sum(row["amount_cents"] for row in scheduled)
    costs_overlap_possible = daily_spending > 0 and any(not row.get("recurring") for row in scheduled)
    everyday_cents = round(daily_spending * horizon_days)
    projected_income = round(daily_income * horizon_days)
    costs = scheduled_cents + everyday_cents
    # Allocate via rounded cumulative totals so the final two-day block and
    # the horizon totals agree exactly, including fractional daily cents.
    series = []
    for offset in range(0, horizon_days, 7) if income_known else []:
        stop = min(offset + 7, horizon_days)
        series.append({
            "week_start": (today + timedelta(days=offset + 1)).isoformat(),
            "days": stop - offset,
            "predicted_income_cents": round(daily_income * stop) - round(daily_income * offset),
        })
    enough_history = weeks >= 6 and (spending_known or bool(scheduled)) and not costs_overlap_possible
    gap = max(0, costs - projected_income - (available_balance_cents or 0))
    status = "insufficient_data" if not enough_history else "planning_gap" if gap else "no_gap_in_estimate"
    target = gap if enough_history else 0
    next_steps = []
    if not enough_history:
        if weeks < 6:
            next_steps.append("record_income")
        if not (spending_known or scheduled):
            next_steps.append("add_upcoming_costs")
        if costs_overlap_possible:
            next_steps.append("review_overlapping_costs")
        if available_balance_cents is None:
            next_steps.append("check_available_cash")
    recommendation_reason = (
        "overlapping_costs" if costs_overlap_possible else
        "insufficient_income_history" if weeks < 6 else
        "insufficient_cost_history" if not (spending_known or scheduled) else
        "planning_gap" if gap else "no_gap_in_estimate"
    )
    reasons = {
        "overlapping_costs": "Upcoming costs may overlap the everyday estimate; distinguish them before using a set-aside recommendation.",
        "insufficient_income_history": "At least six completed weeks of recorded income history are needed for a set-aside recommendation.",
        "insufficient_cost_history": "Add dated upcoming costs or spending records spanning at least 14 recent calendar days before using a set-aside recommendation.",
        "planning_gap": "Estimated costs exceed estimated income and the stated available cash; the difference is a conditional planning gap.",
        "no_gap_in_estimate": "These inputs show no gap over the whole horizon. That does not establish that every bill can be paid on time.",
    }
    assumptions = [
        "Weeks without recorded earnings count as zero inside the observed window; missing entries can lower the estimate.",
        "Only the last eight completed weeks are used. The current partial week and future income are excluded.",
        "Future dated costs are counted once. Marking a past expense recurring does not create a due date or repeat it.",
        "Everyday spending uses up to 30 recorded calendar days, only when the record spans at least 14 days. Unrecorded costs are unknown.",
        "Weekly income does not tell us which day a payout will arrive. No shortfall date or probability is predicted.",
        "Upcoming non-recurring entries may overlap the everyday estimate. When both exist, costs are a conservative combined scenario and no gap recommendation is issued.",
    ]
    assumptions.append(
        "Available cash is unknown. The planning gap assumes no cash is available; recorded net income is not a bank balance."
        if available_balance_cents is None else
        "The cash scenario uses the available amount you entered, not a bank-verified balance."
    )
    explanation = (
        f"This is a planning estimate from {weeks} completed weeks, not a prediction of earnings. "
        f"It covers tomorrow through {end.isoformat()}. "
        + reasons[recommendation_reason] + " "
        + "Past recurring bills need an explicit upcoming entry before they are included as due costs."
    )
    past_income = _valid_rows(incomes, "received_on")
    recorded_net = sum(row["amount_cents"] for row in past_income if row["day"] <= today) - sum(row["amount_cents"] for row in expense_rows if row["day"] <= today)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "horizon_days": horizon_days,
        "horizon_start": (today + timedelta(days=1)).isoformat(),
        "horizon_end": end.isoformat(),
        "predicted_income_cents": projected_income,
        "predicted_expenses_cents": costs,
        "scheduled_expenses_cents": scheduled_cents,
        "everyday_expenses_cents": everyday_cents,
        "available_balance_cents": available_balance_cents,
        "recorded_net_cents": recorded_net,
        "history_weeks": weeks,
        "expense_history_days": observed_days,
        "income_estimate_available": income_known,
        "everyday_estimate_available": spending_known,
        "costs_overlap_possible": costs_overlap_possible,
        "recommendation_reason": recommendation_reason,
        "next_steps": next_steps,
        "calculation": {
            "income_history_cents": sum(row["amount_cents"] for row in completed),
            "income_history_days": weeks * 7,
            "cash_assumed_cents": available_balance_cents or 0,
        },
        "shortfall": {"likely": False, "date": None, "amount_cents": gap if enough_history else 0, "status": status},
        "set_aside": {
            # Integer ceiling preserves cents without a float conversion.
            "weekly_cents": (target * 7 + horizon_days - 1) // horizon_days,
            "total_cents": target,
            "reason": (
                "A conditional planning gap, assuming the stated available cash. This weekly pace does not establish affordability or guarantee savings."
                if target else
                "No additional set-aside is indicated by this horizon estimate. Check individual bill dates and available cash."
                if enough_history else
                "No recommendation is available from these inputs; check your upcoming bills and cash."
            ),
        },
        "confidence": "low",
        "model": {"method": "pandas_weekly_mean", "training_weeks": weeks, "reason": "unvalidated_baseline"},
        "explanation": explanation,
        "assumptions": assumptions,
        "series": series,
    }
