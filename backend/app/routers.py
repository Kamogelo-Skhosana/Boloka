from fastapi import APIRouter, Depends

from .auth import get_current_user_id

router = APIRouter()

# These are stub endpoints that return example data shaped per docs/api.md.
# They are protected by the auth dependency so the contract and wiring are real;
# the database reads and the forecasting model land in later tickets
# (#15 CRUD, #16-#21 the forecasting engine).


@router.get("/me")
def me(user_id: str = Depends(get_current_user_id)):
    return {"id": user_id}


@router.get("/income")
def list_income(user_id: str = Depends(get_current_user_id)):
    return {"items": []}


@router.get("/forecast")
def forecast(user_id: str = Depends(get_current_user_id)):
    # Example shape only. Replaced by the real forecasting engine.
    return {
        "generated_at": None,
        "horizon_days": 30,
        "predicted_income_cents": 0,
        "predicted_expenses_cents": 0,
        "shortfall": {"likely": False, "date": None, "amount_cents": 0},
        "set_aside": {"weekly_cents": 0, "reason": ""},
        "confidence": "low",
        "explanation": "Not enough data yet.",
        "series": [],
    }


@router.get("/summary")
def summary(user_id: str = Depends(get_current_user_id)):
    return {
        "balance_cents": 0,
        "this_week_income_cents": 0,
        "set_aside_progress_cents": 0,
        "set_aside_target_cents": 0,
        "next_shortfall": None,
    }
