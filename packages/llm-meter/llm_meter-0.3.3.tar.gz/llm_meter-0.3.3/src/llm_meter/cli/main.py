import asyncio
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from llm_meter.cli.exporters import get_exporter
from llm_meter.cli.models import UsageExport
from llm_meter.storage import get_storage

app = typer.Typer(help="LLM Usage & Cost Tracking CLI")
usage_app = typer.Typer(help="Inspect LLM usage data")
app.add_typer(usage_app, name="usage")

console = Console()


@usage_app.command("summary")
def summary(
    storage_url: str = typer.Option("sqlite+aiosqlite:///llm_usage.db", "--storage-url", "-s", help="Database URL"),
) -> None:
    """Show a high-level summary of LLM usage by model."""

    async def run() -> list[dict[str, Any]]:
        storage = get_storage(storage_url)
        data = await storage.get_usage_summary()
        await storage.close()
        return data

    data = asyncio.run(run())

    if not data:
        console.print("[yellow]No usage data found.[/yellow]")
        return

    table = Table(title="LLM Usage Summary")
    table.add_column("Model", style="cyan")
    table.add_column("Total Tokens", justify="right")
    table.add_column("Est. Cost ($)", justify="right", style="green")
    table.add_column("Call Count", justify="right")

    for row in data:
        table.add_row(str(row["model"]), f"{row['total_tokens']:,}", f"{row['total_cost']:.6f}", str(row["call_count"]))

    console.print(table)


@usage_app.command("by-endpoint")
def by_endpoint(
    storage_url: str = typer.Option("sqlite+aiosqlite:///llm_usage.db", "--storage-url", "-s", help="Database URL"),
) -> None:
    """Show LLM usage aggregated by endpoint."""

    async def run() -> list[dict[str, Any]]:
        storage = get_storage(storage_url)
        data = await storage.get_usage_by_endpoint()
        await storage.close()
        return data

    data = asyncio.run(run())

    if not data:
        console.print("[yellow]No usage data found.[/yellow]")
        return

    table = Table(title="Usage by Endpoint")
    table.add_column("Endpoint", style="cyan")
    table.add_column("Total Tokens", justify="right")
    table.add_column("Est. Cost ($)", justify="right", style="green")

    for row in data:
        table.add_row(str(row["endpoint"] or "N/A"), f"{row['total_tokens']:,}", f"{row['total_cost']:.6f}")

    console.print(table)


@app.command("export")
def export(
    format: str = typer.Option("json", "--format", "-f", help="Export format (json, csv, excel)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    storage_url: str = typer.Option("sqlite+aiosqlite:///llm_usage.db", "--storage-url", "-s", help="Database URL"),
) -> None:
    """Export raw usage data."""

    async def run() -> list[UsageExport]:
        storage = get_storage(storage_url)
        all_usage = await storage.get_all_usage()
        # Convert SQLAlchemy objects to Pydantic models
        rows = [UsageExport.model_validate(u, from_attributes=True) for u in all_usage]
        await storage.close()
        return rows

    data: list[UsageExport] = asyncio.run(run())

    if not data:
        console.print("[yellow]No data to export.[/yellow]")
        return

    try:
        exporter = get_exporter(format)
        exported_bytes = exporter.export(data)

        if output:
            with open(output, "wb") as f:
                f.write(exported_bytes)
            console.print(f"[green]Data exported to {output}[/green]")
        else:
            # For stdout, attempt to decode if it's text-based (json/csv)
            if format.lower() in ("json", "csv"):
                console.print(exported_bytes.decode("utf-8"))
            else:
                console.print("[red]Binary output (Excel) can only be written to a file using --output.[/red]")
                raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]Error exporting data: {e}[/red]")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":  # pragma: no cover
    app()
