"""Storage file management commands"""

from datetime import datetime
from pathlib import Path

import httpx
import typer
from rich.console import Console
from rich.table import Table

from ...shared.config import config

console = Console()

storage_app = typer.Typer(name="storage", help="File storage commands")


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


@storage_app.command("list")
def list_files(
    prefix: str = typer.Option("", "--prefix", "-p", help="Filter by prefix/folder"),
    limit: int = typer.Option(100, "--limit", "-n", help="Maximum files to list"),
):
    """List files in your storage bucket."""
    try:
        config.get_client()

        params = {"prefix": prefix, "max_files": limit}

        response = httpx.get(
            f"{config.base_url}/api/v2/external/storage/list-files",
            headers={"Authorization": f"Bearer {config.api_key}"},
            params=params,
            timeout=30.0,
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            if response.status_code == 401:
                console.print("[yellow]Run 'lyceum auth login' to re-authenticate.[/yellow]")
            else:
                console.print(f"[red]{response.content.decode()}[/red]")
            raise typer.Exit(1)

        files = response.json()

        if not files:
            console.print("[dim]No files found.[/dim]")
            if prefix:
                console.print(f"[dim]Prefix filter: {prefix}[/dim]")
            return

        table = Table(title="Storage Files")
        table.add_column("Key", style="cyan")
        table.add_column("Size", style="green", justify="right")
        table.add_column("Last Modified", style="dim")

        for f in files:
            last_mod = f.get("last_modified", "")
            if last_mod:
                try:
                    dt = datetime.fromisoformat(last_mod.replace("Z", "+00:00"))
                    last_mod = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pass

            table.add_row(
                f.get("key", ""),
                format_size(f.get("size", 0)),
                last_mod,
            )

        console.print(table)
        console.print(f"\n[dim]Total: {len(files)} file(s)[/dim]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@storage_app.command("upload")
def upload_file(
    file_path: Path = typer.Argument(..., help="Local file to upload"),
    dest: str = typer.Option(None, "--dest", "-d", help="Destination path in storage (defaults to filename)"),
):
    """Upload a file to your storage bucket."""
    try:
        config.get_client()

        if not file_path.exists():
            console.print(f"[red]Error: File not found: {file_path}[/red]")
            raise typer.Exit(1)

        if not file_path.is_file():
            console.print(f"[red]Error: Not a file: {file_path}[/red]")
            raise typer.Exit(1)

        remote_path = dest or file_path.name
        file_size = file_path.stat().st_size

        console.print(f"[dim]Uploading {file_path.name} ({format_size(file_size)})...[/dim]")

        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            data = {"key": remote_path} if dest else {}

            response = httpx.post(
                f"{config.base_url}/api/v2/external/storage/upload",
                headers={"Authorization": f"Bearer {config.api_key}"},
                files=files,
                data=data,
                timeout=300.0,  # 5 min timeout for large files
            )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            if response.status_code == 401:
                console.print("[yellow]Run 'lyceum auth login' to re-authenticate.[/yellow]")
            else:
                console.print(f"[red]{response.content.decode()}[/red]")
            raise typer.Exit(1)

        result = response.json()
        console.print(f"[green]Uploaded successfully![/green]")
        console.print(f"[dim]Key: {result.get('key')}[/dim]")
        console.print(f"[dim]Size: {format_size(result.get('size', 0))}[/dim]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@storage_app.command("download")
def download_file(
    path: str = typer.Argument(..., help="File path in storage to download"),
    output: Path = typer.Option(None, "--output", "-o", help="Local output path (defaults to filename)"),
):
    """Download a file from your storage bucket."""
    try:
        config.get_client()

        # Default output to the filename part of the path
        output_path = output or Path(path.split("/")[-1])

        console.print(f"[dim]Downloading {path}...[/dim]")

        response = httpx.get(
            f"{config.base_url}/api/v2/external/storage/download/{path}",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=300.0,
        )

        if response.status_code == 404:
            console.print(f"[red]Error: File not found: {path}[/red]")
            raise typer.Exit(1)

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            if response.status_code == 401:
                console.print("[yellow]Run 'lyceum auth login' to re-authenticate.[/yellow]")
            else:
                console.print(f"[red]{response.content.decode()}[/red]")
            raise typer.Exit(1)

        with open(output_path, "wb") as f:
            f.write(response.content)

        console.print(f"[green]Downloaded successfully![/green]")
        console.print(f"[dim]Saved to: {output_path}[/dim]")
        console.print(f"[dim]Size: {format_size(len(response.content))}[/dim]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@storage_app.command("delete")
def delete_file(
    path: str = typer.Argument(..., help="File path in storage to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a file from your storage bucket."""
    try:
        config.get_client()

        if not force:
            confirm = typer.confirm(f"Delete '{path}'?")
            if not confirm:
                console.print("[dim]Cancelled.[/dim]")
                raise typer.Exit(0)

        response = httpx.delete(
            f"{config.base_url}/api/v2/external/storage/delete/{path}",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=30.0,
        )

        if response.status_code == 404:
            console.print(f"[red]Error: File not found: {path}[/red]")
            raise typer.Exit(1)

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            if response.status_code == 401:
                console.print("[yellow]Run 'lyceum auth login' to re-authenticate.[/yellow]")
            else:
                console.print(f"[red]{response.content.decode()}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]Deleted: {path}[/green]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@storage_app.command("delete-folder")
def delete_folder(
    prefix: str = typer.Argument(..., help="Folder prefix to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete all files in a folder (by prefix)."""
    try:
        config.get_client()

        if not force:
            confirm = typer.confirm(f"Delete all files in '{prefix}/'?")
            if not confirm:
                console.print("[dim]Cancelled.[/dim]")
                raise typer.Exit(0)

        response = httpx.delete(
            f"{config.base_url}/api/v2/external/storage/delete-folder/{prefix}",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=60.0,
        )

        if response.status_code == 404:
            console.print(f"[yellow]No files found in folder: {prefix}/[/yellow]")
            raise typer.Exit(0)

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            if response.status_code == 401:
                console.print("[yellow]Run 'lyceum auth login' to re-authenticate.[/yellow]")
            else:
                console.print(f"[red]{response.content.decode()}[/red]")
            raise typer.Exit(1)

        result = response.json()
        console.print(f"[green]{result.get('message')}[/green]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
