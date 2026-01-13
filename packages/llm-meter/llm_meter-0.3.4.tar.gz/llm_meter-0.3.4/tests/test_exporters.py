from datetime import datetime, timezone

import pytest

from llm_meter.cli.exporters import get_exporter
from llm_meter.cli.models import UsageExport


def test_csv_exporter_empty():
    exporter = get_exporter("csv")
    assert exporter.export([]) == b""


def test_excel_exporter_success():
    data = [
        UsageExport(
            request_id="123",
            endpoint="/test",
            user_id="user1",
            model="gpt-4o",
            provider="openai",
            total_tokens=100,
            cost_estimate=0.002,
            latency_ms=500,
            timestamp=datetime.now(timezone.utc),
        )
    ]
    exporter = get_exporter("excel")
    exported_bytes = exporter.export(data)

    assert isinstance(exported_bytes, bytes)
    assert len(exported_bytes) > 0
    # ZIP signature for .xlsx
    assert exported_bytes.startswith(b"PK\x03\x04")


def test_excel_exporter_empty():
    exporter = get_exporter("excel")
    assert exporter.export([]) == b""


def test_excel_exporter_import_error(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "openpyxl":
            raise ImportError("openpyxl not found")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)
    exporter = get_exporter("excel")
    with pytest.raises(ImportError, match="Excel export requires 'openpyxl'"):
        exporter.export(
            [
                UsageExport(
                    request_id="123",
                    endpoint=None,
                    user_id=None,
                    model="model",
                    provider="p",
                    total_tokens=1,
                    cost_estimate=0,
                    latency_ms=1,
                    timestamp=datetime.now(timezone.utc),
                )
            ]
        )


def test_get_exporter_invalid():
    with pytest.raises(ValueError, match="Unsupported format"):
        get_exporter("pdf")
