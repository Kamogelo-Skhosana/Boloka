import csv
import io
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field, field_validator

from .auth import get_current_user_claims, get_current_user_id
from .database import request_table
from .forecasting import build_forecast, local_today

router = APIRouter()


class IncomeCreate(BaseModel):
    amount_cents: int = Field(gt=0, le=2_000_000_000)
    source: str | None = Field(default=None, max_length=120)
    received_on: date
    note: str | None = Field(default=None, max_length=1000)


class IncomePatch(BaseModel):
    amount_cents: int | None = Field(default=None, gt=0, le=2_000_000_000)
    source: str | None = Field(default=None, max_length=120)
    received_on: date | None = None
    note: str | None = Field(default=None, max_length=1000)

    @field_validator("amount_cents", "received_on")
    @classmethod
    def reject_null_required_fields(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("This field cannot be null")
        return value


class ExpenseCreate(BaseModel):
    amount_cents: int = Field(gt=0, le=2_000_000_000)
    category: str | None = Field(default=None, max_length=120)
    spent_on: date
    recurring: bool = False
    note: str | None = Field(default=None, max_length=1000)


class ExpensePatch(BaseModel):
    amount_cents: int | None = Field(default=None, gt=0, le=2_000_000_000)
    category: str | None = Field(default=None, max_length=120)
    spent_on: date | None = None
    recurring: bool | None = None
    note: str | None = Field(default=None, max_length=1000)

    @field_validator("amount_cents", "spent_on", "recurring")
    @classmethod
    def reject_null_required_fields(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("This field cannot be null")
        return value


class SavingsContributionCreate(BaseModel):
    amount_cents: int = Field(gt=0, le=2_000_000_000)
    saved_on: date
    note: str | None = Field(default=None, max_length=120)


def _user_uuid(user_id: str) -> str:
    try:
        return str(UUID(user_id))
    except ValueError as exc:
        raise HTTPException(status_code=401, detail={"error": {"code": "invalid_token", "message": "Invalid user token"}}) from exc


def _list_entries(table: str, date_field: str, user_id: str, start: date | None, end: date | None):
    if start and end and start > end:
        raise HTTPException(status_code=422, detail={"error": {"code": "validation_error", "message": "The from date must be on or before the to date"}})
    filters: dict[str, str] = {"order": f"{date_field}.desc,created_at.desc"}
    if start and end:
        filters["and"] = f"({date_field}.gte.{start.isoformat()},{date_field}.lte.{end.isoformat()})"
    elif start:
        filters[date_field] = f"gte.{start.isoformat()}"
    elif end:
        filters[date_field] = f"lte.{end.isoformat()}"
    return {"items": request_table("GET", table, user_id=user_id, params=filters) or []}


@router.get("/me")
def me(claims: dict = Depends(get_current_user_claims)):
    return {"id": _user_uuid(claims["sub"]), "email": claims.get("email"), "created_at": None}


@router.get("/income")
def list_income(
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    user_id: str = Depends(get_current_user_id),
):
    return _list_entries("income_events", "received_on", _user_uuid(user_id), from_, to)


@router.post("/income", status_code=status.HTTP_201_CREATED)
def create_income(body: IncomeCreate, user_id: str = Depends(get_current_user_id)):
    data = body.model_dump(mode="json") | {"user_id": _user_uuid(user_id)}
    rows = request_table("POST", "income_events", user_id=user_id, payload=data, prefer="return=representation")
    return rows[0]


@router.patch("/income/{entry_id}")
def update_income(entry_id: UUID, body: IncomePatch, user_id: str = Depends(get_current_user_id)):
    fields = body.model_dump(mode="json", exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail={"error": {"code": "empty_patch", "message": "Provide at least one field to update"}})
    rows = request_table("PATCH", "income_events", user_id=_user_uuid(user_id), params={"id": f"eq.{entry_id}"}, payload=fields, prefer="return=representation")
    if not rows:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Income entry not found"}})
    return rows[0]


@router.delete("/income/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(entry_id: UUID, user_id: str = Depends(get_current_user_id)):
    rows = request_table("DELETE", "income_events", user_id=_user_uuid(user_id), params={"id": f"eq.{entry_id}", "select": "id"}, prefer="return=representation")
    if not rows:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Income entry not found"}})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _parse_amount(value: str) -> int:
    try:
        amount = Decimal(value.strip().replace("R", "").replace(",", ""))
    except InvalidOperation as exc:
        raise ValueError("amount must be a valid number") from exc
    cents = int((amount * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    if cents <= 0 or cents > 2_000_000_000:
        raise ValueError("amount must be greater than zero and within the supported limit")
    return cents


@router.post("/income/import")
async def import_income(file: UploadFile = File(...), user_id: str = Depends(get_current_user_id)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail={"error": {"code": "invalid_file", "message": "Upload a .csv file"}})
    raw = await file.read(2_000_001)
    if len(raw) > 2_000_000:
        raise HTTPException(status_code=413, detail={"error": {"code": "file_too_large", "message": "CSV files must be 2 MB or smaller"}})
    try:
        text = raw.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        required = {"amount", "source", "received_on"}
        if not reader.fieldnames or not required.issubset({name.strip() for name in reader.fieldnames}):
            raise ValueError("CSV needs amount, source and received_on columns")
    except (UnicodeDecodeError, csv.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail={"error": {"code": "invalid_csv", "message": str(exc)}}) from exc

    imported = 0
    skipped = 0
    owner = _user_uuid(user_id)
    batch: list[dict[str, Any]] = []
    for row in reader:
        try:
            amount = _parse_amount(row.get("amount", ""))
            received_on = date.fromisoformat((row.get("received_on") or "").strip())
            batch.append({
                "user_id": owner,
                "amount_cents": amount,
                "source": (row.get("source") or "").strip()[:120] or None,
                "received_on": received_on.isoformat(),
                "note": (row.get("note") or "").strip()[:1000] or None,
            })
        except (ValueError, TypeError):
            skipped += 1
    if batch:
        request_table("POST", "income_events", user_id=owner, payload=batch, prefer="return=minimal")
        imported = len(batch)
    return {"imported": imported, "skipped": skipped}


@router.get("/expenses")
def list_expenses(
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    user_id: str = Depends(get_current_user_id),
):
    return _list_entries("expenses", "spent_on", _user_uuid(user_id), from_, to)


@router.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(body: ExpenseCreate, user_id: str = Depends(get_current_user_id)):
    data = body.model_dump(mode="json") | {"user_id": _user_uuid(user_id)}
    rows = request_table("POST", "expenses", user_id=user_id, payload=data, prefer="return=representation")
    return rows[0]


@router.patch("/expenses/{entry_id}")
def update_expense(entry_id: UUID, body: ExpensePatch, user_id: str = Depends(get_current_user_id)):
    fields = body.model_dump(mode="json", exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail={"error": {"code": "empty_patch", "message": "Provide at least one field to update"}})
    rows = request_table("PATCH", "expenses", user_id=_user_uuid(user_id), params={"id": f"eq.{entry_id}"}, payload=fields, prefer="return=representation")
    if not rows:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Expense entry not found"}})
    return rows[0]


@router.delete("/expenses/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(entry_id: UUID, user_id: str = Depends(get_current_user_id)):
    rows = request_table("DELETE", "expenses", user_id=_user_uuid(user_id), params={"id": f"eq.{entry_id}", "select": "id"}, prefer="return=representation")
    if not rows:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Expense entry not found"}})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/savings")
def list_savings(
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    user_id: str = Depends(get_current_user_id),
):
    return _list_entries("savings_contributions", "saved_on", _user_uuid(user_id), from_, to)


@router.post("/savings", status_code=status.HTTP_201_CREATED)
def create_savings_contribution(body: SavingsContributionCreate, user_id: str = Depends(get_current_user_id)):
    data = body.model_dump(mode="json") | {"user_id": _user_uuid(user_id)}
    rows = request_table("POST", "savings_contributions", user_id=user_id, payload=data, prefer="return=representation")
    return rows[0]


@router.delete("/savings/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_savings_contribution(entry_id: UUID, user_id: str = Depends(get_current_user_id)):
    rows = request_table("DELETE", "savings_contributions", user_id=_user_uuid(user_id), params={"id": f"eq.{entry_id}", "select": "id"}, prefer="return=representation")
    if not rows:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Savings entry not found"}})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


class ForecastScenario(BaseModel):
    available_balance_cents: int | None = Field(default=None, ge=0, le=2_000_000_000, strict=True)


def _user_forecast(user_id: str, available_balance_cents: int | None = None) -> dict:
    owner = _user_uuid(user_id)
    incomes = request_table("GET", "income_events", user_id=owner, params={"select": "amount_cents,received_on", "order": "received_on.asc"}) or []
    expenses = request_table("GET", "expenses", user_id=owner, params={"select": "amount_cents,spent_on,recurring,category", "order": "spent_on.asc"}) or []
    return build_forecast(incomes, expenses, available_balance_cents=available_balance_cents)


@router.get("/forecast")
def forecast(user_id: str = Depends(get_current_user_id)) -> dict:
    return _user_forecast(user_id)


@router.post("/forecast/scenario")
def forecast_scenario(body: ForecastScenario, user_id: str = Depends(get_current_user_id)) -> dict:
    # Scenario cash is neither persisted nor placed in URLs/access logs.
    return _user_forecast(user_id, body.available_balance_cents)


@router.get("/summary")
def summary(user_id: str = Depends(get_current_user_id)):
    owner = _user_uuid(user_id)
    incomes = request_table("GET", "income_events", user_id=owner, params={"select": "amount_cents,received_on"}) or []
    expenses = request_table("GET", "expenses", user_id=owner, params={"select": "amount_cents,spent_on,recurring,category"}) or []
    savings = request_table("GET", "savings_contributions", user_id=owner, params={"select": "amount_cents,saved_on"}) or []
    today = local_today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    week_income = sum(
        int(item["amount_cents"])
        for item in incomes
        if week_start <= date.fromisoformat(item["received_on"]) <= today
    )
    recorded_balance = sum(
        int(item["amount_cents"])
        for item in incomes
        if date.fromisoformat(item["received_on"]) <= today
    ) - sum(
        int(item["amount_cents"])
        for item in expenses
        if date.fromisoformat(item["spent_on"]) <= today
    )
    model = build_forecast(incomes, expenses, today=today)
    gap = model["shortfall"]
    return {
        "balance_cents": recorded_balance,
        "this_week_income_cents": week_income,
        "set_aside_progress_cents": sum(
            int(item["amount_cents"])
            for item in savings
            if month_start <= date.fromisoformat(item["saved_on"]) <= today
        ),
        "set_aside_target_cents": model["set_aside"]["total_cents"],
        "next_shortfall": {"date": gap["date"], "amount_cents": gap["amount_cents"]} if gap["likely"] else None,
    }
