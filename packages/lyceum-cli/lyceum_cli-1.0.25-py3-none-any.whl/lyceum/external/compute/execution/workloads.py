"""Workload management commands: list jobs, abort, history"""

import httpx
import typer
from rich.console import Console
from rich.table import Table

from ....shared.config import config

console = Console()

workloads_app = typer.Typer(name="workloads", help="Workload management commands")


def truncate_id(execution_id: str, length: int = 8) -> str:
    """Truncate execution ID for display."""
    if not execution_id:
        return "N/A"
    return execution_id[:length] if len(execution_id) > length else execution_id


def format_timestamp(ts: str | None) -> str:
    """Format timestamp for display."""
    if not ts:
        return "N/A"
    # Simple formatting - just return the date portion
    return ts[:19].replace("T", " ") if len(ts) >= 19 else ts


def create_table(title: str, columns: list[dict]) -> Table:
    """Create a rich table with the given columns."""
    table = Table(title=title)
    for col in columns:
        table.add_column(
            col["header"],
            style=col.get("style"),
            no_wrap=col.get("no_wrap", False),
            max_width=col.get("max_width"),
        )
    return table


@workloads_app.command("list")
def list_jobs(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of executions to show"),
):
    """List currently running executions"""
    try:
        config.get_client()

        response = httpx.get(
            f"{config.base_url}/api/v2/external/workloads/list",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=30.0,
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            if response.content:
                console.print(f"[red]{response.content.decode()}[/red]")
            raise typer.Exit(1)

        executions = response.json()
        if not isinstance(executions, list):
            executions = []

        executions = executions[:limit]

        if not executions:
            console.print("[dim]No running executions found[/dim]")
            return

        columns = [
            {"header": "ID", "style": "cyan", "no_wrap": True, "max_width": 12},
            {"header": "Status", "style": "yellow"},
            {"header": "File", "style": "magenta"},
            {"header": "Hardware", "style": "dim"},
            {"header": "Started", "style": "dim"},
        ]

        table = create_table("Running Executions", columns)

        for execution in executions:
            table.add_row(
                truncate_id(execution.get("execution_id", "N/A"), 8),
                execution.get("status", "N/A"),
                execution.get("file_name", "N/A"),
                execution.get("hardware_profile", "N/A"),
                format_timestamp(execution.get("created_at")),
            )

        console.print(table)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@workloads_app.command("abort")
def abort(
    execution_id: str = typer.Argument(..., help="Execution ID to abort"),
):
    """Abort a running execution"""
    try:
        config.get_client()

        response = httpx.post(
            f"{config.base_url}/api/v2/external/workloads/abort/{execution_id}",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=30.0,
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            if response.content:
                console.print(f"[red]{response.content.decode()}[/red]")
            raise typer.Exit(1)

        result = response.json()
        message = result.get("message", "Execution aborted") if isinstance(result, dict) else "Execution aborted"
        console.print(f"[green]{message}[/green]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@workloads_app.command("history")
def history(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of executions to show"),
):
    """Show your execution history"""
    try:
        config.get_client()

        response = httpx.get(
            f"{config.base_url}/api/v2/external/billing/history",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=30.0,
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            if response.content:
                console.print(f"[red]{response.content.decode()}[/red]")
            raise typer.Exit(1)

        data = response.json()
        executions = data.get("executions", [])[:limit] if isinstance(data, dict) else []

        if not executions:
            console.print("[dim]No execution history found[/dim]")
            return

        columns = [
            {"header": "ID", "style": "cyan", "no_wrap": True, "max_width": 12},
            {"header": "Status", "style": "green"},
            {"header": "File", "style": "yellow"},
            {"header": "Machine", "style": "magenta"},
            {"header": "Created", "style": "dim"},
        ]

        table = create_table("Execution History", columns)

        for execution in executions:
            table.add_row(
                truncate_id(execution.get("execution_id", "N/A"), 8),
                execution.get("status", "N/A"),
                execution.get("file_name", "N/A"),
                execution.get("hardware_profile", "N/A"),
                format_timestamp(execution.get("created_at")),
            )

        console.print(table)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
