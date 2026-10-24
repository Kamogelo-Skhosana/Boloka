"""Explainable, low-data cash-flow forecast for irregular income.

This baseline deliberately avoids fitting an overconfident time-series model
to a short, noisy gig-income history. It uses a weekly pandas aggregation,
recent weighted income, known recurring expenses, and a visible confidence
level. A learned model can replace the estimator when validated history exists.
"""

from collections.abc import Iterable
from datetime import date, datetime, timedelta, timezone
from statistics import median
from typing import Any

import pandas as pd


def weekly_income(events: Iterable[dict[str, Any]], today: date) -> list[dict[str, Any]]:
    rows = [
        {"date": event["received_on"], "amount_cents": int(event["amount_cents"])}
        for event in events
    ]
    if not rows:
        return []
    frame = pd.DataFrame(rows)
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame.dropna(subset=["date"])
    frame = frame[frame["date"].dt.date <= today]
    if frame.empty:
        return []
    frame["week_start"] = frame["date"].dt.to_period("W-SUN").dt.start_time.dt.date
    grouped = frame.groupby("week_start", as_index=False)["amount_cents"].sum()
    return [
        {"week_start": row.week_start.isoformat(), "amount_cents": int(row.amount_cents)}
        for row in grouped.itertuples(index=False)
    ]


def build_forecast(
    incomes: list[dict[str, Any]],
    expenses: list[dict[str, Any]],
    *,
    today: date | None = None,
    horizon_days: int = 30,
) -> dict[str, Any]:
    today = today or datetime.now(timezone.utc).date()
    weekly = weekly_income(incomes, today)
    recent = [row["amount_cents"] for row in weekly[-8:]]
    history_weeks = len(weekly)
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
        f"Based on {history_weeks} weeks of recorded income, your recent weekly "
        f"average is R{weekly_income_cents / 100:,.2f}. Known costs over the next "
        f"month are about R{predicted_expenses / 100:,.2f}. "
    )
    if history_weeks < 6:
        explanation += "This is an early estimate because there are fewer than six weeks of income history. Add more entries to improve it."
    elif gap:
        explanation += "The estimate shows a likely gap; setting aside a little each week can build a buffer."
    else:
        explanation += "No shortfall is visible in this estimate; keep recording income and expenses to track changes."

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
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
