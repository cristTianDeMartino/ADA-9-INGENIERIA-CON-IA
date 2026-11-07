"""Integration tests for the CLI interface (AC-01 to AC-06, VR-01 to VR-03)."""
import json
import pytest
from src.customer_search.cli import main, DEFAULT_DATA_FILE


def test_cli_search_by_name(capsys):
    ret = main(["garcia", "--field", "name"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Found 2 customer(s) matching 'garcia'" in captured.out
    assert "Ana Sofia Garcia" in captured.out
    assert "Carlos Alberto Ramirez Garcia" in captured.out


def test_cli_search_by_email(capsys):
    ret = main(["innovatech.mx", "--field", "email"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Found 2 customer(s)" in captured.out
    assert "ana.garcia@innovatech.mx" in captured.out
    assert "hortiz@innovatech.mx" in captured.out


def test_cli_search_unified_all(capsys):
    # Matches cust-001, cust-002, cust-003
    ret = main(["garcia"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Found 3 customer(s) matching 'garcia' [field: all]:" in captured.out
    assert "Beatriz Elena Mendez" in captured.out


def test_cli_search_json_output(capsys):
    ret = main(["torres", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["query"] == "torres"
    assert data["total_matches"] == 1
    assert data["customers"][0]["name"] == "Elena Maria Torres"
    assert data["customers"][0]["email"] == "elena.torres@acmewidgets.com"


def test_cli_zero_matches(capsys):
    ret = main(["nonexistentterm"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "No customers found matching 'nonexistentterm'." in captured.out


def test_cli_validation_error_short_query(capsys):
    # VR-02 / AC-04 / FR-04: Length < 2
    ret = main(["a"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: Search query must contain at least 2 non-whitespace characters." in captured.err
    assert "Traceback" not in captured.err


def test_cli_validation_error_whitespace_query(capsys):
    # VR-01 / AC-04 / FR-04: Whitespace only
    ret = main(["   "])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: Search query must contain at least 2 non-whitespace characters." in captured.err
    assert "Traceback" not in captured.err


def test_cli_data_file_not_found(capsys):
    ret = main(["garcia", "-d", "nonexistent_file_abc.json"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: Customer data file not found" in captured.err
    assert "Traceback" not in captured.err


def test_cli_invalid_field_option(capsys):
    # Argparse handles this and exits with code 2
    ret = main(["garcia", "--field", "invalid_field"])
    assert ret == 2
    captured = capsys.readouterr()
    assert "invalid choice" in captured.err


def test_cli_active_only_flag(capsys):
    # CR-01: --active-only filters out inactive customers
    ret = main(["garcia", "--active-only", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    for cust in data["customers"]:
        assert cust["is_active"] is True

