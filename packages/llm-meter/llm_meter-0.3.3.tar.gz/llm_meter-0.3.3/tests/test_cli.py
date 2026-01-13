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
