import asyncio
import json

import pytest
from typer.testing import CliRunner

from llm_meter.cli.main import app
from llm_meter.models import LLMUsage
from llm_meter.storage import StorageManager

runner = CliRunner()


@pytest.fixture
def temp_db(tmp_path):
    """Fixture for an empty database."""
    db_path = tmp_path / "test_empty.db"
    url = f"sqlite+aiosqlite:///{db_path}"

    async def init():
        sm = StorageManager(url)
        await sm.initialize()
        await sm.close()

    asyncio.run(init())
    return url


@pytest.fixture
def seeded_db(tmp_path):
    """Fixture for a database with sample usage records."""
    db_path = tmp_path / "test_seeded.db"
    url = f"sqlite+aiosqlite:///{db_path}"

    async def seed():
        sm = StorageManager(url)
        await sm.initialize()
        u1 = LLMUsage(
            request_id="1", model="gpt-4o", provider="openai", total_tokens=100, cost_estimate=0.1, endpoint="/chat"
        )
        u2 = LLMUsage(
            request_id="2",
            model="gpt-4o-mini",
            provider="openai",
            total_tokens=50,
            cost_estimate=0.01,
            endpoint="/chat",
        )
        await sm.record_usage(u1)
        await sm.record_usage(u2)
        await sm.close()

    asyncio.run(seed())
    return url


# --- Basic / Main ---


def test_cli_main_entry():
    """Verify that the CLI help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "LLM Usage & Cost Tracking CLI" in result.stdout


# --- Empty State Tests ---


def test_cli_summary_empty(temp_db):
    """Verify summary command with no data."""
    result = runner.invoke(app, ["usage", "summary", "-s", temp_db])
    assert result.exit_code == 0
    assert "No usage data found" in result.stdout


def test_cli_by_endpoint_empty(temp_db):
    """Verify by-endpoint command with no data."""
    result = runner.invoke(app, ["usage", "by-endpoint", "-s", temp_db])
    assert result.exit_code == 0
    assert "No usage data found" in result.stdout


def test_cli_export_empty(temp_db):
    """Verify export command with no data."""
    result = runner.invoke(app, ["export", "-s", temp_db])
    assert result.exit_code == 0
    assert "No data to export" in result.stdout


# --- Data Presentation Tests ---


def test_cli_summary_with_data(seeded_db):
    """Verify summary table formatting with data."""
    result = runner.invoke(app, ["usage", "summary", "-s", seeded_db])
    assert result.exit_code == 0
    assert "gpt-4o" in result.stdout
    assert "0.100000" in result.stdout


def test_cli_by_endpoint_with_data(seeded_db):
    """Verify by-endpoint table formatting with data."""
    result = runner.invoke(app, ["usage", "by-endpoint", "-s", seeded_db])
    assert result.exit_code == 0
    assert "/chat" in result.stdout
    assert "150" in result.stdout


# --- Export Tests ---


def test_cli_export_json_stdout(seeded_db):
    """Verify JSON export to stdout."""
    result = runner.invoke(app, ["export", "-s", seeded_db, "--format", "json"])
    assert result.exit_code == 0
    assert "gpt-4o" in result.stdout
    # Ensure it's valid JSON
    data = json.loads(result.stdout)
    assert len(data) == 2


def test_cli_export_json_file(seeded_db, tmp_path):
    """Verify JSON export to a file."""
    out_file = tmp_path / "out.json"
    result = runner.invoke(app, ["export", "-s", seeded_db, "--format", "json", "-o", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()

    data = json.loads(out_file.read_text())
    assert len(data) == 2
    assert data[0]["request_id"] == "1"


def test_cli_export_csv_stdout(seeded_db):
    """Verify CSV export to stdout."""
    result = runner.invoke(app, ["export", "-s", seeded_db, "--format", "csv"])
    assert result.exit_code == 0
    assert "request_id,endpoint,user_id,model,provider" in result.stdout
    assert "1,/,openai,gpt-4o,openai" in result.stdout or "1,/chat" in result.stdout


def test_cli_export_csv_file(seeded_db, tmp_path):
    """Verify CSV export to a file."""
    out_file = tmp_path / "out.csv"
    result = runner.invoke(app, ["export", "-s", seeded_db, "--format", "csv", "-o", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "gpt-4o" in content
    assert "gpt-4o-mini" in content


def test_cli_export_excel_no_output(seeded_db):
    """Verify Excel export fails without --output."""
    result = runner.invoke(app, ["export", "-s", seeded_db, "--format", "excel"])
    assert result.exit_code == 1
    assert "Binary output (Excel) can only be written to a file" in result.stdout


def test_cli_export_excel_file(seeded_db, tmp_path):
    """Verify Excel export to a file."""
    out_file = tmp_path / "out.xlsx"
    result = runner.invoke(app, ["export", "-s", seeded_db, "--format", "excel", "-o", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    assert out_file.read_bytes().startswith(b"PK\x03\x04")


def test_cli_export_unsupported_format(seeded_db):
    """Verify error on unsupported format."""
    result = runner.invoke(app, ["export", "-s", seeded_db, "--format", "unsupported"])
    assert result.exit_code == 1
    assert "Error exporting data: Unsupported format: unsupported" in result.stdout


# --- Budget Commands Tests ---


def test_cli_budget_set_basic(temp_db):
    """Verify budget set command with basic options."""
    result = runner.invoke(app, ["budget", "set", "testuser", "100.0", "-s", temp_db])
    assert result.exit_code == 0
    assert "Budget set for user 'testuser'" in result.stdout
    assert "Monthly limit: $100.00" in result.stdout
    assert "Blocking: disabled" in result.stdout


def test_cli_budget_set_with_daily_limit(temp_db):
    """Verify budget set command with daily limit."""
    result = runner.invoke(app, ["budget", "set", "testuser", "100.0", "--daily-limit", "10.0", "-s", temp_db])
    assert result.exit_code == 0
    assert "Daily limit: $10.00" in result.stdout


def test_cli_budget_set_with_blocking(temp_db):
    """Verify budget set command with blocking enabled."""
    result = runner.invoke(app, ["budget", "set", "testuser", "100.0", "--blocking", "-s", temp_db])
    assert result.exit_code == 0
    assert "Blocking: enabled" in result.stdout


def test_cli_budget_set_with_warning(temp_db):
    """Verify budget set command with custom warning threshold."""
    result = runner.invoke(app, ["budget", "set", "testuser", "100.0", "--warning", "0.5", "-s", temp_db])
    assert result.exit_code == 0
    assert "Warning threshold: 50%" in result.stdout


def test_cli_budget_status_not_configured(temp_db):
    """Verify budget status when no budget is configured."""
    result = runner.invoke(app, ["budget", "status", "nonexistent", "-s", temp_db])
    assert result.exit_code == 0
    assert "No budget configured for user 'nonexistent'" in result.stdout


def test_cli_budget_status_configured(temp_db, seeded_db):
    """Verify budget status with configured budget."""
    # First set a budget
    runner.invoke(app, ["budget", "set", "testuser", "100.0", "-s", seeded_db])

    result = runner.invoke(app, ["budget", "status", "testuser", "-s", seeded_db])
    assert result.exit_code == 0
    assert "Budget Status for User: testuser" in result.stdout
    assert "Limit: $100.00" in result.stdout
    assert "Blocking: disabled" in result.stdout


def test_cli_budget_list_empty(temp_db):
    """Verify budget list when no budgets configured."""
    result = runner.invoke(app, ["budget", "list", "-s", temp_db])
    assert result.exit_code == 0
    assert "No budgets configured" in result.stdout


def test_cli_budget_list_with_budgets(temp_db, seeded_db):
    """Verify budget list with configured budgets."""
    # First set a budget
    runner.invoke(app, ["budget", "set", "user1", "100.0", "--daily-limit", "10.0", "-s", seeded_db])
    runner.invoke(app, ["budget", "set", "user2", "200.0", "--blocking", "-s", seeded_db])

    result = runner.invoke(app, ["budget", "list", "-s", seeded_db])
    assert result.exit_code == 0
    assert "user1" in result.stdout
    assert "user2" in result.stdout
    assert "$100.00" in result.stdout
    assert "$10.00" in result.stdout
    assert "Yes" in result.stdout  # blocking enabled
    assert "No" in result.stdout  # blocking disabled


def test_cli_budget_delete(temp_db, seeded_db):
    """Verify budget delete command."""
    # First set a budget
    runner.invoke(app, ["budget", "set", "testuser", "100.0", "-s", seeded_db])

    result = runner.invoke(app, ["budget", "delete", "testuser", "-s", seeded_db])
    assert result.exit_code == 0
    assert "Budget deleted for user 'testuser'" in result.stdout

    # Verify it's deleted
    result = runner.invoke(app, ["budget", "status", "testuser", "-s", seeded_db])
    assert "No budget configured" in result.stdout


def test_cli_budget_delete_nonexistent(temp_db):
    """Verify budget delete for nonexistent user doesn't error."""
    result = runner.invoke(app, ["budget", "delete", "nonexistent", "-s", temp_db])
    assert result.exit_code == 0
    assert "Budget deleted for user 'nonexistent'" in result.stdout


@pytest.fixture
def budget_db_no_limit(tmp_path):
    """Fixture for a database with a budget that has no limits configured."""
    db_path = tmp_path / "test_no_limit.db"
    url = f"sqlite+aiosqlite:///{db_path}"

    async def init():
        from llm_meter.models import Budget

        sm = StorageManager(url)
        await sm.initialize()
        # Create a budget with no limits (both monthly_limit and daily_limit are None)
        budget = Budget(
            user_id="nolimit_user",
            monthly_limit=None,  # No limit set
            daily_limit=None,  # No limit set
            blocking_enabled=False,
            warning_threshold=0.8,
        )
        await sm.upsert_budget(budget)
        await sm.close()

    asyncio.run(init())
    return url


def test_cli_budget_status_unlimited(budget_db_no_limit):
    """Verify budget status shows 'Limit: Unlimited' when no limits are configured."""
    result = runner.invoke(app, ["budget", "status", "nolimit_user", "-s", budget_db_no_limit])
    assert result.exit_code == 0
    assert "Budget Status for User: nolimit_user" in result.stdout
    assert "Limit: Unlimited" in result.stdout
