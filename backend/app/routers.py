from datetime import date, timedelta
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

from .auth import get_current_access_token, get_current_user_claims, get_current_user_id
from .csv_import import CsvImportError, ParsedIncome, parse_income_csv
from .database import request_table
from .forecast_schema import ForecastResponse
from .forecasting import build_forecast, local_today
from .schemas import IncomeCreate

router = APIRouter()


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


def _list_entries(table: str, date_field: str, user_id: str, start: date | None, end: date | None, access_token: str):
    if start and end and start > end:
        raise HTTPException(status_code=422, detail={"error": {"code": "validation_error", "message": "The from date must be on or before the to date"}})
    filters: dict[str, str] = {"order": f"{date_field}.desc,created_at.desc"}
    if start and end:
        filters["and"] = f"({date_field}.gte.{start.isoformat()},{date_field}.lte.{end.isoformat()})"
    elif start:
        filters[date_field] = f"gte.{start.isoformat()}"
    elif end:
        filters[date_field] = f"lte.{end.isoformat()}"
    return {"items": request_table("GET", table, access_token=access_token, user_id=user_id, params=filters) or []}


@router.get("/me")
def me(claims: dict = Depends(get_current_user_claims)):
    return {"id": _user_uuid(claims["sub"]), "email": claims.get("email"), "created_at": None}


@router.get("/income")
def list_income(
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token),
):
    return _list_entries("income_events", "received_on", _user_uuid(user_id), from_, to, access_token)


@router.post("/income", status_code=status.HTTP_201_CREATED)
def create_income(body: IncomeCreate, user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)):
    data = body.model_dump(mode="json") | {"user_id": _user_uuid(user_id)}
    rows = request_table("POST", "income_events", access_token=access_token, user_id=user_id, payload=data, prefer="return=representation")
    return rows[0]


@router.patch("/income/{entry_id}")
def update_income(entry_id: UUID, body: IncomePatch, user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)):
    fields = body.model_dump(mode="json", exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail={"error": {"code": "empty_patch", "message": "Provide at least one field to update"}})
    rows = request_table("PATCH", "income_events", access_token=access_token, user_id=_user_uuid(user_id), params={"id": f"eq.{entry_id}"}, payload=fields, prefer="return=representation")
    if not rows:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Income entry not found"}})
    return rows[0]


@router.delete("/income/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(entry_id: UUID, user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)):
    rows = request_table("DELETE", "income_events", access_token=access_token, user_id=_user_uuid(user_id), params={"id": f"eq.{entry_id}", "select": "id"}, prefer="return=representation")
    if not rows:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Income entry not found"}})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def _parse_income_upload(file: UploadFile, owner: str) -> ParsedIncome:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail={"error": {"code": "invalid_file", "message": "Upload a .csv file"}})
    raw = await file.read(2_000_001)
    if len(raw) > 2_000_000:
        raise HTTPException(status_code=413, detail={"error": {"code": "file_too_large", "message": "CSV files must be 2 MB or smaller"}})
    try:
        return parse_income_csv(raw, owner)
    except CsvImportError as exc:
        raise HTTPException(status_code=400, detail={"error": {"code": "invalid_csv", "message": str(exc)}}) from exc


@router.post("/income/import")
async def import_income(file: UploadFile = File(...), user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)):
    owner = _user_uuid(user_id)
    result = await _parse_income_upload(file, owner)
    if result.rows:
        request_table("POST", "income_events", access_token=access_token, user_id=owner, payload=result.rows, prefer="return=minimal")
    return {"imported": len(result.rows), "skipped": result.skipped, "errors": result.errors}


@router.post("/income/import/preview")
async def preview_income_import(file: UploadFile = File(...), user_id: str = Depends(get_current_user_id)) -> dict:
    result = await _parse_income_upload(file, _user_uuid(user_id))
    return {
        "rows": [{**{key: value for key, value in row.items() if key != "user_id"}, "line": line}
                 for row, line in zip(result.rows, result.line_numbers)],
        "skipped": result.skipped,
        "errors": result.errors,
    }


class IncomeImportConfirmation(BaseModel):
    rows: list[IncomeCreate] = Field(min_length=1, max_length=10_000)


@router.post("/income/import/confirm")
def confirm_income_import(body: IncomeImportConfirmation, user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)) -> dict:
    owner = _user_uuid(user_id)
    # Revalidate the whole edited batch before writing; never accept uploaded ownership.
    rows = [row.model_dump(mode="json") | {"user_id": owner} for row in body.rows]
    request_table("POST", "income_events", access_token=access_token, user_id=owner, payload=rows, prefer="return=minimal")
    return {"imported": len(rows), "skipped": 0, "errors": []}


@router.get("/expenses")
def list_expenses(
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token),
):
    return _list_entries("expenses", "spent_on", _user_uuid(user_id), from_, to, access_token)


@router.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(body: ExpenseCreate, user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)):
    data = body.model_dump(mode="json") | {"user_id": _user_uuid(user_id)}
    rows = request_table("POST", "expenses", access_token=access_token, user_id=user_id, payload=data, prefer="return=representation")
    return rows[0]


@router.patch("/expenses/{entry_id}")
def update_expense(entry_id: UUID, body: ExpensePatch, user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)):
    fields = body.model_dump(mode="json", exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail={"error": {"code": "empty_patch", "message": "Provide at least one field to update"}})
    rows = request_table("PATCH", "expenses", access_token=access_token, user_id=_user_uuid(user_id), params={"id": f"eq.{entry_id}"}, payload=fields, prefer="return=representation")
    if not rows:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Expense entry not found"}})
    return rows[0]


@router.delete("/expenses/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(entry_id: UUID, user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)):
    rows = request_table("DELETE", "expenses", access_token=access_token, user_id=_user_uuid(user_id), params={"id": f"eq.{entry_id}", "select": "id"}, prefer="return=representation")
    if not rows:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Expense entry not found"}})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/savings")
def list_savings(
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token),
):
    return _list_entries("savings_contributions", "saved_on", _user_uuid(user_id), from_, to, access_token)


@router.post("/savings", status_code=status.HTTP_201_CREATED)
def create_savings_contribution(body: SavingsContributionCreate, user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)):
    data = body.model_dump(mode="json") | {"user_id": _user_uuid(user_id)}
    rows = request_table("POST", "savings_contributions", access_token=access_token, user_id=user_id, payload=data, prefer="return=representation")
    return rows[0]


@router.delete("/savings/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_savings_contribution(entry_id: UUID, user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)):
    rows = request_table("DELETE", "savings_contributions", access_token=access_token, user_id=_user_uuid(user_id), params={"id": f"eq.{entry_id}", "select": "id"}, prefer="return=representation")
    if not rows:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Savings entry not found"}})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


class ForecastScenario(BaseModel):
    available_balance_cents: int | None = Field(default=None, ge=0, le=2_000_000_000, strict=True)


def _user_forecast(user_id: str, available_balance_cents: int | None = None, *, access_token: str) -> dict:
    owner = _user_uuid(user_id)
    incomes = request_table("GET", "income_events", access_token=access_token, user_id=owner, params={"select": "amount_cents,received_on", "order": "received_on.asc"}) or []
    expenses = request_table("GET", "expenses", access_token=access_token, user_id=owner, params={"select": "amount_cents,spent_on,recurring,category", "order": "spent_on.asc"}) or []
    return build_forecast(incomes, expenses, available_balance_cents=available_balance_cents)


@router.get("/forecast", response_model=ForecastResponse)
def forecast(user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)) -> dict:
    return _user_forecast(user_id, access_token=access_token)


@router.post("/forecast/scenario", response_model=ForecastResponse)
def forecast_scenario(body: ForecastScenario, user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)) -> dict:
    # Scenario cash is neither persisted nor placed in URLs/access logs.
    return _user_forecast(user_id, body.available_balance_cents, access_token=access_token)


@router.get("/summary")
def summary(user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)):
    owner = _user_uuid(user_id)
    incomes = request_table("GET", "income_events", access_token=access_token, user_id=owner, params={"select": "amount_cents,received_on"}) or []
    expenses = request_table("GET", "expenses", access_token=access_token, user_id=owner, params={"select": "amount_cents,spent_on,recurring,category"}) or []
    savings = request_table("GET", "savings_contributions", access_token=access_token, user_id=owner, params={"select": "amount_cents,saved_on"}) or []
    today = local_today()
    model = build_forecast(incomes, expenses, today=today)
    return _build_summary(incomes, expenses, savings, today=today, model=model)


def _build_summary(incomes: list[dict], expenses: list[dict], savings: list[dict], *, today: date, model: dict) -> dict:
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


class DashboardResponse(BaseModel):
    summary: dict[str, Any]
    forecast: ForecastResponse
    income: list[dict[str, Any]]
    expenses: list[dict[str, Any]]
    savings: list[dict[str, Any]]


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(user_id: str = Depends(get_current_user_id), access_token: str = Depends(get_current_access_token)) -> dict:
    owner = _user_uuid(user_id)
    incomes = _list_entries("income_events", "received_on", owner, None, None, access_token)["items"]
    expenses = _list_entries("expenses", "spent_on", owner, None, None, access_token)["items"]
    savings = _list_entries("savings_contributions", "saved_on", owner, None, None, access_token)["items"]
    today = local_today()
    model = build_forecast(incomes, expenses, today=today)
    return {
        "summary": _build_summary(incomes, expenses, savings, today=today, model=model),
        "forecast": model,
        "income": incomes,
        "expenses": expenses,
        "savings": savings,
    }
