import pytest
from fastapi.testclient import TestClient

from app import csv_import, routers
from app.auth import get_current_access_token, get_current_user_id
from app.csv_import import CsvImportError, parse_amount, parse_income_csv
from app.main import app

OWNER = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


@pytest.mark.parametrize("value,cents", [("10", 1000), ("R 1,234.56", 123456), ("0.01", 1), ("20,000,000", 2_000_000_000)])
def test_exact_money(value, cents):
    assert parse_amount(value) == cents


@pytest.mark.parametrize("value", ["NaN", "sNaN", "Infinity", "Inf", "-1", "0", "R", "1,2", "1.001", "1E100000", "1R2", "20,000,000.01", "9" * 1000])
def test_invalid_money_is_rejected_without_decimal_exceptions(value):
    with pytest.raises(ValueError):
        parse_amount(value)


def test_bom_normalized_headers_and_caller_ownership():
    parsed = parse_income_csv(b'\xef\xbb\xbf Amount , SOURCE, received_on ,note,user_id\n"R1,234.56",Test,2026-10-24,Hello,other-user\n', OWNER)
    assert parsed.rows == [{"amount_cents": 123456, "source": "Test", "received_on": "2026-10-24", "note": "Hello", "user_id": OWNER}]
    assert parsed.skipped == 0


def test_bad_rows_report_lines_without_echoing_data_or_truncating_text():
    csv = "amount,source,received_on,note\n10,Good,2026-10-24,OK\nNaN,Private label,2026-10-24,Secret note\n10,Long,2026-02-30,no\n10,Test,2026-10-24," + "x" * 1001
    parsed = parse_income_csv(csv.encode(), OWNER)
    assert len(parsed.rows) == 1
    assert parsed.skipped == 3
    assert [error["line"] for error in parsed.errors] == [3, 4, 5]
    assert "Private label" not in str(parsed.errors)
    assert "Secret note" not in str(parsed.errors)


@pytest.mark.parametrize("raw", [
    b"amount, source, SOURCE,received_on\n1,a,b,2026-10-24\n",
    b"amount,source\n1,a\n", b"\xff\xfeinvalid",
    b'amount,source,received_on\n10,Good,2026-10-24\n10,"unfinished,2026-10-24',
])
def test_file_errors_do_not_return_a_partial_batch(raw):
    with pytest.raises(CsvImportError):
        parse_income_csv(raw, OWNER)


def test_row_limit_fails_entire_file_and_errors_are_bounded(monkeypatch):
    raw = b"amount,source,received_on\n" + b"NaN,Test,2026-10-24\n" * 15
    parsed = parse_income_csv(raw, OWNER)
    assert parsed.skipped == 15
    assert len(parsed.errors) == 10
    monkeypatch.setattr(csv_import, "MAX_ROWS", 2)
    with pytest.raises(CsvImportError, match="no more than"):
        parse_income_csv(raw, OWNER)


def test_column_mismatch_and_invalid_dates_are_skipped():
    raw = b"amount,source,received_on\n10,Too,Many,Columns\n10,Compact,20261024\n10,Test,2026-10-24\n"
    parsed = parse_income_csv(raw, OWNER)
    assert parsed.skipped == 2
    assert len(parsed.rows) == 1


def test_import_endpoint_does_not_write_a_malformed_file(monkeypatch):
    app.dependency_overrides[get_current_user_id] = lambda: OWNER
    app.dependency_overrides[get_current_access_token] = lambda: "test-token"
    monkeypatch.setattr(routers, "request_table", lambda *a, **k: pytest.fail("Malformed file must not be saved"))
    try:
        response = TestClient(app).post("/api/v1/income/import", files={"file": ("history.csv", b'amount,source,received_on\n10,Good,2026-10-24\n10,"unfinished', "text/csv")})
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "invalid_csv"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("filename,raw,expected", [
    ("history.txt", b"amount,source,received_on\n10,Test,2026-10-24\n", 400),
    ("history.csv", b"x" * 2_000_001, 413),
], ids=["wrong-extension", "oversized-upload"])
def test_file_boundaries_reject_before_database(monkeypatch, filename, raw, expected):
    app.dependency_overrides[get_current_user_id] = lambda: OWNER
    app.dependency_overrides[get_current_access_token] = lambda: "test-token"
    monkeypatch.setattr(routers, "request_table", lambda *a, **k: pytest.fail("Rejected upload must not be saved"))
    try:
        response = TestClient(app).post("/api/v1/income/import", files={"file": (filename, raw, "text/csv")})
        assert response.status_code == expected
    finally:
        app.dependency_overrides.clear()
