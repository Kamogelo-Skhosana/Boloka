"""Explainable, low-data cash-flow forecast for irregular income.

This baseline deliberately avoids fitting an overconfident time-series model
to a short, noisy gig-income history. It uses a weekly pandas aggregation,
recent weighted income, known recurring expenses, and a visible confidence
level. A learned model can replace the estimator when validated history exists.
"""

from collections.abc import Iterable
from datetime import UTC, date, datetime, timedelta
from statistics import median
from typing import Any

import pandas as pd


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
    weeks = pd.date_range(grouped.index.min(), current_week, freq="W-MON")
    grouped = grouped.reindex(weeks, fill_value=0)
    return [
        {"week_start": week.date().isoformat(), "amount_cents": int(amount)}
        for week, amount in grouped.items()
    ]


def build_forecast(
    incomes: list[dict[str, Any]],
    expenses: list[dict[str, Any]],
    *,
    today: date | None = None,
    horizon_days: int = 30,
) -> dict[str, Any]:
    today = today or datetime.now(UTC).date()
    weekly = weekly_income(incomes, today)
    current_week = (today - timedelta(days=today.weekday())).isoformat()
    completed = [row for row in weekly if row["week_start"] < current_week]
    # Do not treat an unfinished week as a full week's earning pattern. If no
    # completed week exists, use this week's recorded total as a cold start.
    recent = [row["amount_cents"] for row in (completed or weekly)[-8:]]
    history_weeks = len(completed)
    confidence = "high" if history_weeks >= 12 else "medium" if history_weeks >= 6 else "low"
    # Weighted average gives recent work a larger influence while reducing the
    # effect of one unusually large payout.
    if recent:
        weights = list(range(1, len(recent) + 1))
        weekly_income_cents = round(sum(v * w for v, w in zip(recent, weights)) / sum(weights))
        weekly_income_cents = min(weekly_income_cents, round(median(recent) * 2))
    else:
        weekly_income_cents = 0

    lookback = today - timedelta(days=30)
    recent_expenses = [
        int(row["amount_cents"])
        for row in expenses
        if date.fromisoformat(str(row["spent_on"])) >= lookback
    ]
    monthly_expenses = sum(recent_expenses)
    recurring_categories: dict[str, list[int]] = {}
    for row in expenses:
        if row.get("recurring") and date.fromisoformat(str(row["spent_on"])) >= today - timedelta(days=90):
            category = str(row.get("category") or "other recurring cost").strip().lower()
            recurring_categories.setdefault(category, []).append(int(row["amount_cents"]))
    recurring_monthly = sum(round(median(amounts)) for amounts in recurring_categories.values())
    # For a cold start, still account for fixed known costs without projecting
    # unobserved discretionary spending.
    predicted_income = weekly_income_cents * max(1, round(horizon_days / 7))
    predicted_expenses = max(monthly_expenses, recurring_monthly, 0)
    gap = max(0, predicted_expenses - predicted_income)
    shortfall_date = today + timedelta(days=min(horizon_days, 21)) if gap else None
    weekly_saving = round(gap / max(1, (shortfall_date - today).days // 7)) if gap else 0

    series = []
    for week in range(max(1, (horizon_days + 6) // 7)):
        start = today + timedelta(days=week * 7)
        series.append({
            "week_start": start.isoformat(),
            "predicted_income_cents": weekly_income_cents,
            "lower_cents": round(weekly_income_cents * 0.5),
            "upper_cents": round(weekly_income_cents * 1.5),
        })

    explanation = (
        f"Based on {history_weeks} completed weeks of recorded income, your recent weekly "
        f"average is R{weekly_income_cents / 100:,.2f}. Known costs over the next "
        f"month are about R{predicted_expenses / 100:,.2f}. "
    )
    if weekly and not completed:
        explanation += "With no completed week yet, this uses only the income recorded so far this week. "
    if history_weeks < 6:
        explanation += "This is an early estimate because there are fewer than six weeks of income history. Add more entries to improve it."
    elif gap:
        explanation += "The estimate shows a likely gap; setting aside a little each week can build a buffer."
    else:
        explanation += "No shortfall is visible in this estimate; keep recording income and expenses to track changes."

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "horizon_days": horizon_days,
        "predicted_income_cents": predicted_income,
        "predicted_expenses_cents": predicted_expenses,
        "shortfall": {
            "likely": bool(gap),
            "date": shortfall_date.isoformat() if shortfall_date else None,
            "amount_cents": gap,
        },
        "set_aside": {
            "weekly_cents": weekly_saving,
            "reason": (
                f"Saving about R{weekly_saving / 100:,.2f} each week builds toward the estimated gap."
                if gap else "No set-aside is suggested from the current estimate."
            ),
        },
        "confidence": confidence,
        "explanation": explanation,
        "series": series,
    }
