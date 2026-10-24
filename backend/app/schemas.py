from datetime import date

from pydantic import BaseModel, Field


class IncomeCreate(BaseModel):
    amount_cents: int = Field(gt=0, le=2_000_000_000)
    source: str | None = Field(default=None, max_length=120)
    received_on: date
    note: str | None = Field(default=None, max_length=1000)
