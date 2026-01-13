import asyncio
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from llm_meter.budget import BudgetManager
from llm_meter.cli.exporters import get_exporter
from llm_meter.cli.models import UsageExport
from llm_meter.models import Budget
from llm_meter.storage import get_storage

app = typer.Typer(help="LLM Usage & Cost Tracking CLI")
usage_app = typer.Typer(help="Inspect LLM usage data")
app.add_typer(usage_app, name="usage")
budget_app = typer.Typer(help="Manage user budgets")
app.add_typer(budget_app, name="budget")

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


# Budget CLI commands


@budget_app.command("set")
def budget_set(
    user_id: str = typer.Argument(..., help="User ID"),
    monthly_limit: float = typer.Argument(..., help="Monthly budget limit in USD"),
    daily_limit: float | None = typer.Option(None, "--daily-limit", "-d", help="Daily budget limit in USD"),
    blocking: bool = typer.Option(False, "--blocking", "-b", help="Block requests when budget exceeded"),
    warning_threshold: float = typer.Option(0.8, "--warning", "-w", help="Warning threshold (0.0-1.0, default 0.8)"),
    storage_url: str = typer.Option("sqlite+aiosqlite:///llm_usage.db", "--storage-url", "-s"),
) -> None:
    """Set a budget for a user."""

    async def run() -> None:
        storage = get_storage(storage_url)
        await storage.initialize()  # Create tables if needed
        budget = Budget(
            user_id=user_id,
            monthly_limit=monthly_limit,
            daily_limit=daily_limit,
            blocking_enabled=blocking,
            warning_threshold=warning_threshold,
        )
        await storage.upsert_budget(budget)
        await storage.close()
        console.print(f"[green]Budget set for user '{user_id}'[/green]")
        console.print(f"  Monthly limit: ${monthly_limit:.2f}")
        if daily_limit:
            console.print(f"  Daily limit: ${daily_limit:.2f}")
        console.print(f"  Blocking: {'enabled' if blocking else 'disabled'}")
        console.print(f"  Warning threshold: {warning_threshold * 100:.0f}%")

    asyncio.run(run())


@budget_app.command("status")
def budget_status(
    user_id: str = typer.Argument(..., help="User ID"),
    storage_url: str = typer.Option("sqlite+aiosqlite:///llm_usage.db", "--storage-url", "-s"),
) -> None:
    """Show current budget status for a user."""

    async def run() -> None:
        storage = get_storage(storage_url)
        await storage.initialize()  # Create tables if needed
        manager = BudgetManager(storage)
        status = await manager.get_budget_status(user_id)
        await storage.close()

        if not status["budget_configured"]:
            console.print(f"[yellow]No budget configured for user '{user_id}'[/yellow]")
            return

        console.print(f"Budget Status for User: {user_id}")
        console.print("-" * 40)

        limit = status["limit"]
        if limit:
            console.print(f"Limit: ${limit:.2f}")
        else:
            console.print("Limit: Unlimited")

        console.print(f"Current Spend: ${status['current_spend']:.4f}")

        if limit:
            console.print(f"Percentage Used: {status['percentage_used']:.1f}%")
            remaining = status["remaining_budget"]
            if remaining is not None:
                console.print(f"Remaining: ${remaining:.4f}")

        console.print(f"Period: {status['period_start'][:19]} to {status['period_end'][:19]}")
        console.print(f"Blocking: {'enabled' if status['blocking_enabled'] else 'disabled'}")

    asyncio.run(run())


@budget_app.command("list")
def budget_list(
    storage_url: str = typer.Option("sqlite+aiosqlite:///llm_usage.db", "--storage-url", "-s"),
) -> None:
    """List all configured budgets."""

    async def run() -> None:
        storage = get_storage(storage_url)
        await storage.initialize()  # Create tables if needed
        budgets = await storage.get_all_budgets()
        await storage.close()

        if not budgets:
            console.print("[yellow]No budgets configured.[/yellow]")
            return

        table = Table(title="Configured Budgets")
        table.add_column("User ID", style="cyan")
        table.add_column("Monthly Limit", justify="right", style="green")
        table.add_column("Daily Limit", justify="right", style="green")
        table.add_column("Blocking", justify="center")

        for budget in budgets:
            table.add_row(
                budget.user_id,
                f"${budget.monthly_limit:.2f}" if budget.monthly_limit else "N/A",
                f"${budget.daily_limit:.2f}" if budget.daily_limit else "N/A",
                "Yes" if budget.blocking_enabled else "No",
            )

        console.print(table)

    asyncio.run(run())


@budget_app.command("delete")
def budget_delete(
    user_id: str = typer.Argument(..., help="User ID"),
    storage_url: str = typer.Option("sqlite+aiosqlite:///llm_usage.db", "--storage-url", "-s"),
) -> None:
    """Delete a user's budget configuration."""

    async def run() -> None:
        storage = get_storage(storage_url)
        await storage.initialize()  # Create tables if needed
        await storage.delete_budget(user_id)
        await storage.close()
        console.print(f"[green]Budget deleted for user '{user_id}'[/green]")

    asyncio.run(run())


if __name__ == "__main__":  # pragma: no cover
    app()
