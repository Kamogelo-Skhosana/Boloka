"""Public contract for the inspectable cash-planning baseline."""

from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field

Cents = Annotated[int, Field(ge=0, strict=True)]
Reason = Literal["insufficient_income_history", "insufficient_cost_history",
                 "overlapping_costs", "planning_gap", "no_gap_in_estimate"]
NextStep = Literal["record_income", "add_upcoming_costs", "review_overlapping_costs", "check_available_cash"]


class Shortfall(BaseModel):
    likely: Literal[False]
    date: None
    amount_cents: Cents
    status: Literal["insufficient_data", "planning_gap", "no_gap_in_estimate"]


class SetAside(BaseModel):
    weekly_cents: Cents
    total_cents: Cents
    reason: str


class Calculation(BaseModel):
    income_history_cents: Cents
    income_history_days: Annotated[int, Field(ge=0, le=56)]
    cash_assumed_cents: Cents


class Baseline(BaseModel):
    method: Literal["pandas_weekly_mean"]
    training_weeks: Annotated[int, Field(ge=0, le=8)]
    reason: Literal["unvalidated_baseline"]


class IncomeBlock(BaseModel):
    week_start: date
    days: Annotated[int, Field(ge=1, le=7)]
    predicted_income_cents: Cents


class ForecastResponse(BaseModel):
    generated_at: datetime
    horizon_days: Annotated[int, Field(ge=1, le=90)]
    horizon_start: date
    horizon_end: date
    predicted_income_cents: Cents
    predicted_expenses_cents: Cents
    scheduled_expenses_cents: Cents
    everyday_expenses_cents: Cents
    available_balance_cents: Cents | None
    recorded_net_cents: int
    history_weeks: Annotated[int, Field(ge=0, le=8)]
    expense_history_days: Annotated[int, Field(ge=0, le=30)]
    income_estimate_available: bool
    everyday_estimate_available: bool
    costs_overlap_possible: bool
    recommendation_reason: Reason
    next_steps: list[NextStep]
    calculation: Calculation
    shortfall: Shortfall
    set_aside: SetAside
    confidence: Literal["low"]
    model: Baseline
    explanation: str
    assumptions: list[str]
    series: list[IncomeBlock]
