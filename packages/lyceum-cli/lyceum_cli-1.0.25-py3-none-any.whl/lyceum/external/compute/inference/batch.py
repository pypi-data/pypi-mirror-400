"""OpenAI-compatible batch processing commands"""

import os
from pathlib import Path

import httpx
import typer
from rich.console import Console

from ....shared.config import config
from ....shared.display import create_table, format_timestamp, truncate_id

console = Console()

batch_app = typer.Typer(name="batch", help="OpenAI-compatible batch processing")


@batch_app.command("upload")
def upload_file(
    file_path: str = typer.Argument(..., help="Path to JSONL file to upload"),
    purpose: str = typer.Option("batch", "--purpose", "-p", help="File purpose (batch, batch_output, batch_errors)"),
):
    """Upload a JSONL file for batch processing"""
    # Check if file exists
    if not Path(file_path).exists():
        console.print(f"[red]Error: File '{file_path}' not found[/red]")
        raise typer.Exit(1)

    # Validate file extension
    if not file_path.endswith('.jsonl'):
        console.print("[yellow]Warning: File doesn't have .jsonl extension[/yellow]")

    try:
        console.print(f"[dim]📤 Uploading {os.path.basename(file_path)} for {purpose}...[/dim]")

        # Upload file using multipart form data
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/jsonl')}
            data = {'purpose': purpose}

            response = httpx.post(
                f"{config.base_url}/api/v2/external/files",
                headers={"Authorization": f"Bearer {config.api_key}"},
                files=files,
                data=data,
                timeout=60.0
            )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            console.print(f"[red]{response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()

        console.print("[green]✅ File uploaded successfully![/green]")
        console.print(f"[cyan]File ID: {data['id']}[/cyan]")
        console.print(f"[dim]Size: {data['bytes']} bytes[/dim]")
        console.print(f"[dim]Purpose: {data['purpose']}[/dim]")
        console.print(f"[dim]Created: {data['created_at']}[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@batch_app.command("create")
def create_batch(
    input_file_id: str = typer.Argument(..., help="File ID of uploaded JSONL file"),
    endpoint: str | None = typer.Option(
        None, "--endpoint", "-e", help="API endpoint (optional, uses URLs from JSONL if not specified)"
    ),
    model: str | None = typer.Option(
        None, "--model", "-m", help="Model to use for all requests (overrides model in JSONL)"
    ),
    completion_window: str = typer.Option(
        "24h", "--completion-window", "-w", help="Completion window (24h only)"
    ),
):
    """Create a batch processing job"""
    try:
        console.print(f"[dim]🚀 Creating batch job for file {input_file_id}...[/dim]")

        request_data = {
            "input_file_id": input_file_id,
            "completion_window": completion_window
        }

        # Only include endpoint if explicitly provided as override
        if endpoint:
            request_data["endpoint"] = endpoint
            console.print(f"[dim]Using endpoint override: {endpoint}[/dim]")
        # Note: endpoint is NOT required - the API should use URLs from JSONL file

        # Include model override if specified
        if model:
            request_data["model"] = model
            console.print(f"[dim]Using model override: {model}[/dim]")

        response = httpx.post(
            f"{config.base_url}/api/v2/external/batches",
            headers={"Authorization": f"Bearer {config.api_key}"},
            json=request_data,
            timeout=30.0
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            console.print(f"[red]{response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()

        console.print("[green]✅ Batch job created successfully![/green]")
        console.print(f"[cyan]Batch ID: {data['id']}[/cyan]")
        console.print(f"[yellow]Status: {data['status']}[/yellow]")
        console.print(f"[dim]Endpoint: {data['endpoint']}[/dim]")
        console.print(f"[dim]Input File ID: {data['input_file_id']}[/dim]")
        console.print(f"[dim]Expires: {data['expires_at']}[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@batch_app.command("get")
def get_batch(
    batch_id: str = typer.Argument(..., help="Batch ID to retrieve"),
):
    """Get batch job status and details"""
    try:
        console.print(f"[dim]🔍 Retrieving batch {batch_id}...[/dim]")

        response = httpx.get(
            f"{config.base_url}/api/v2/external/batches/{batch_id}",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=30.0
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            console.print(f"[red]{response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()

        # Status color coding
        status = data['status']
        if status == "completed":
            status_color = "green"
        elif status in ["failed", "expired", "cancelled"]:
            status_color = "red"
        elif status in ["in_progress", "finalizing"]:
            status_color = "yellow"
        else:
            status_color = "dim"

        console.print(f"[cyan]Batch ID: {data['id']}[/cyan]")
        console.print(f"[{status_color}]Status: {status}[/{status_color}]")
        console.print(f"[dim]Endpoint: {data['endpoint']}[/dim]")
        console.print(f"[dim]Input File: {data['input_file_id']}[/dim]")

        if data.get('output_file_id'):
            console.print(f"[green]Output File: {data['output_file_id']}[/green]")

        if data.get('error_file_id'):
            console.print(f"[red]Error File: {data['error_file_id']}[/red]")

        # Request statistics
        counts = data.get('request_counts', {})
        console.print(
            f"[dim]Requests - Total: {counts.get('total', 0)}, "
            f"Completed: {counts.get('completed', 0)}, "
            f"Failed: {counts.get('failed', 0)}[/dim]"
        )

        # Timestamps
        console.print(f"[dim]Created: {data.get('created_at', 'N/A')}[/dim]")
        if data.get('completed_at'):
            console.print(f"[dim]Completed: {data['completed_at']}[/dim]")
        if data.get('expires_at'):
            console.print(f"[dim]Expires: {data['expires_at']}[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@batch_app.command("list")
def list_batches(
    after: str | None = typer.Option(None, "--after", help="List batches after this batch ID"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of batches to return"),
):
    """List batch jobs"""
    try:
        console.print("[dim]📋 Listing batch jobs...[/dim]")

        params = {"limit": limit}
        if after:
            params["after"] = after

        response = httpx.get(
            f"{config.base_url}/api/v2/external/batches",
            headers={"Authorization": f"Bearer {config.api_key}"},
            params=params,
            timeout=30.0
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            console.print(f"[red]{response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()
        batches = data.get('data', [])

        if not batches:
            console.print("[dim]No batch jobs found[/dim]")
            return

        columns = [
            {"header": "Batch ID", "style": "cyan", "no_wrap": True, "max_width": 16},
            {"header": "Status", "style": "yellow"},
            {"header": "Endpoint", "style": "green"},
            {"header": "Requests", "style": "magenta", "justify": "center"},
            {"header": "Created", "style": "dim"}
        ]

        table = create_table("Batch Jobs", columns)

        for batch in batches:
            batch_id = batch['id']
            short_id = truncate_id(batch_id, 12)

            counts = batch.get('request_counts', {})
            request_stats = f"{counts.get('completed', 0)}/{counts.get('total', 0)}"

            table.add_row(
                short_id,
                batch['status'],
                batch['endpoint'],
                request_stats,
                format_timestamp(batch.get('created_at'))
            )

        console.print(table)
        console.print(f"\n[dim]Found {len(batches)} batch jobs[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@batch_app.command("cancel")
def cancel_batch(
    batch_id: str = typer.Argument(..., help="Batch ID to cancel"),
):
    """Cancel a batch job"""
    try:
        console.print(f"[dim]🛑 Cancelling batch {batch_id}...[/dim]")

        response = httpx.post(
            f"{config.base_url}/api/v2/external/batches/{batch_id}/cancel",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=30.0
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            console.print(f"[red]{response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()

        console.print("[green]✅ Batch cancelled successfully![/green]")
        console.print(f"[cyan]Batch ID: {data['id']}[/cyan]")
        console.print(f"[yellow]Status: {data['status']}[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@batch_app.command("download")
def download_file(
    file_id: str = typer.Argument(..., help="File ID to download"),
    output_file: str | None = typer.Option(
        None, "--output", "-o", help="Output file path (prints to console if not specified)"
    ),
):
    """Download batch file content (input, output, or error files)"""
    try:
        console.print(f"[dim]⬇️  Downloading file {file_id}...[/dim]")

        response = httpx.get(
            f"{config.base_url}/api/v2/external/files/{file_id}/content",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=60.0
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            console.print(f"[red]{response.text}[/red]")
            raise typer.Exit(1)

        content = response.text

        if output_file:
            # Save to file
            with open(output_file, 'w') as f:
                f.write(content)
            console.print(f"[green]✅ Content saved to {output_file}[/green]")
            console.print(f"[dim]Size: {len(content)} characters[/dim]")
        else:
            # Print to console
            console.print("[green]📄 File Content:[/green]")
            console.print("-" * 50)
            console.print(content)
            console.print("-" * 50)
            console.print(f"[dim]Size: {len(content)} characters[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
