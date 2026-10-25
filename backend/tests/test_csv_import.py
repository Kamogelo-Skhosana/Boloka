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
@pytest.mark.parametrize("path", ["/income/import", "/income/import/preview"])
def test_file_boundaries_reject_before_database(monkeypatch, filename, raw, expected, path):
    app.dependency_overrides[get_current_user_id] = lambda: OWNER
    app.dependency_overrides[get_current_access_token] = lambda: "test-token"
    monkeypatch.setattr(routers, "request_table", lambda *a, **k: pytest.fail("Rejected upload must not be saved"))
    try:
        response = TestClient(app).post("/api/v1" + path, files={"file": (filename, raw, "text/csv")})
        assert response.status_code == expected
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def import_client():
    app.dependency_overrides[get_current_user_id] = lambda: OWNER
    app.dependency_overrides[get_current_access_token] = lambda: "test-token"
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_preview_has_line_numbers_and_never_writes(import_client, monkeypatch):
    monkeypatch.setattr(routers, "request_table", lambda *a, **k: pytest.fail("Preview cannot touch the database"))
    raw = b'amount,source,received_on,note,user_id\n10,Good,2026-10-24,Hello,other\ninvalid,Bad,2026-10-24,,other\n\n20,Next,2026-10-23,,other\n'
    response = import_client.post("/api/v1/income/import/preview", files={"file": ("history.csv", raw, "text/csv")})
    assert response.status_code == 200
    body = response.json()
    assert body["skipped"] == 1
    assert [row["line"] for row in body["rows"]] == [2, 5]
    assert [row["amount_cents"] for row in body["rows"]] == [1000, 2000]
    assert all("user_id" not in row for row in body["rows"])


def test_malformed_preview_cannot_write(import_client, monkeypatch):
    monkeypatch.setattr(routers, "request_table", lambda *a, **k: pytest.fail("Preview cannot write"))
    response = import_client.post("/api/v1/income/import/preview", files={"file": ("history.csv", b'amount,source,received_on\n10,Good,2026-10-24\n10,"unfinished', "text/csv")})
    assert response.status_code == 400


def test_confirmation_revalidates_and_owns_the_entire_batch(import_client, monkeypatch):
    calls = []
    monkeypatch.setattr(routers, "request_table", lambda *a, **k: calls.append((a, k)))
    response = import_client.post("/api/v1/income/import/confirm", json={"rows": [
        {"amount_cents": 1250, "source": "Corrected", "received_on": "2026-10-24", "note": "Reviewed", "user_id": "other"},
    ]})
    assert response.status_code == 200
    assert response.json()["imported"] == 1
    assert len(calls) == 1
    assert calls[0][0] == ("POST", "income_events")
    assert calls[0][1]["access_token"] == "test-token"
    assert calls[0][1]["user_id"] == OWNER
    assert calls[0][1]["payload"] == [{"amount_cents": 1250, "source": "Corrected", "received_on": "2026-10-24", "note": "Reviewed", "user_id": OWNER}]


@pytest.mark.parametrize("rows", [[], [
    {"amount_cents": 1000, "received_on": "2026-10-24"},
    {"amount_cents": -1, "received_on": "2026-02-30"},
]])
def test_invalid_confirmation_writes_nothing(import_client, monkeypatch, rows):
    monkeypatch.setattr(routers, "request_table", lambda *a, **k: pytest.fail("Invalid batch cannot write even its valid rows"))
    assert import_client.post("/api/v1/income/import/confirm", json={"rows": rows}).status_code == 422


@pytest.mark.parametrize("path", ["preview", "confirm"])
def test_review_routes_require_auth(path):
    assert TestClient(app).post("/api/v1/income/import/" + path).status_code == 401


def test_oversized_confirmation_is_rejected_before_writes(import_client, monkeypatch):
    monkeypatch.setattr(routers, "request_table", lambda *a, **k: pytest.fail("Oversized batch cannot write"))
    row = {"amount_cents": 100, "received_on": "2026-10-24"}
    assert import_client.post("/api/v1/income/import/confirm", json={"rows": [row] * 10001}).status_code == 422
