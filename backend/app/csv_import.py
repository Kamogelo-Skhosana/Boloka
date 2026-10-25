"""Parse untrusted income history fully before any database write."""

import csv
import io
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import ValidationError

from .schemas import IncomeCreate

MAX_ROWS = 10_000
MAX_ERRORS = 10


class CsvImportError(ValueError):
    """A file-level problem; no parsed rows may be saved."""


@dataclass(frozen=True)
class ParsedIncome:
    rows: list[dict[str, Any]]
    skipped: int
    errors: list[dict[str, Any]]
    line_numbers: list[int]


def parse_amount(value: str) -> int:
    text = value.strip()
    if text.startswith("R"):
        text = text[1:].strip()
    if len(text) > 32 or not re.fullmatch(r"(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]{1,2})?", text):
        raise ValueError("Use positive rands with a dot and at most two decimal places")
    amount = Decimal(text.replace(",", ""))
    if not 0 < amount <= 20_000_000:
        raise ValueError("Amount must be greater than zero and no more than R20,000,000")
    return int(amount * 100)


def parse_income_csv(raw: bytes, owner: str) -> ParsedIncome:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CsvImportError("Use a UTF-8 CSV file") from exc
    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    line_numbers: list[int] = []
    skipped = 0
    count = 0
    try:
        headers = [column.strip().lower() for column in next(reader, [])]
        if not {"amount", "source", "received_on"}.issubset(headers):
            raise CsvImportError("CSV needs amount, source and received_on columns")
        if len(set(headers)) != len(headers) or any(not name for name in headers):
            raise CsvImportError("CSV column names must be unique and nonempty")
        for values in reader:
            if not values or all(not value.strip() for value in values):
                continue
            count += 1
            if count > MAX_ROWS:
                raise CsvImportError("CSV must contain no more than 10,000 data rows")
            try:
                if len(values) != len(headers):
                    raise ValueError("Row has the wrong number of columns")
                row = dict(zip(headers, values))
                if any("\x00" in value for value in values):
                    raise ValueError("Row contains an unsupported control character")
                received_on = row["received_on"].strip()
                if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", received_on):
                    raise ValueError("Date must use YYYY-MM-DD")
                try:
                    parsed_date = date.fromisoformat(received_on)
                except ValueError as exc:
                    raise ValueError("Date must be a valid calendar date") from exc
                body = IncomeCreate(
                    amount_cents=parse_amount(row["amount"]),
                    source=row["source"].strip() or None,
                    received_on=parsed_date,
                    note=(row.get("note") or "").strip() or None,
                )
                rows.append(body.model_dump(mode="json") | {"user_id": owner})
                line_numbers.append(reader.line_num)
            except ValidationError:
                skipped += 1
                if len(errors) < MAX_ERRORS:
                    errors.append({"line": reader.line_num, "message": "Source must be 120 characters or fewer; note must be 1,000 or fewer"})
            except ValueError as exc:
                skipped += 1
                if len(errors) < MAX_ERRORS:
                    errors.append({"line": reader.line_num, "message": str(exc)})
    except csv.Error as exc:
        raise CsvImportError("Malformed CSV; check quoted fields and column lengths") from exc
    return ParsedIncome(rows, skipped, errors, line_numbers)
