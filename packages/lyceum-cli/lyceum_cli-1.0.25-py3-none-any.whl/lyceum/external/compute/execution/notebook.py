"""
Jupyter Notebook execution commands
"""

from typing import Optional

import httpx
import typer
from rich.console import Console

from ....shared.config import config
from ....shared.streaming import StatusLine

console = Console()

notebook_app = typer.Typer(name="notebook", help="Launch Jupyter notebooks on Lyceum Cloud")

# Pre-built Jupyter notebook image (linux/amd64)
JUPYTER_IMAGE = "jupyter/base-notebook:latest"


@notebook_app.command("launch")
def launch_notebook(
    machine_type: str = typer.Option(
        "cpu", "--machine", "-m", help="Machine type (cpu, a100, h100, etc.)"
    ),
    timeout: int = typer.Option(
        600, "--timeout", "-t", help="Session timeout in seconds (max: 600)"
    ),
    image: Optional[str] = typer.Option(
        None, "--image", "-i", help="Custom Jupyter image (default: jupyter/base-notebook)"
    ),
    token: str = typer.Option(
        "lyceum", "--token", help="Jupyter notebook token for authentication"
    ),
    port: int = typer.Option(
        8888, "--port", "-p", help="Port for Jupyter server"
    ),
):
    """Launch a Jupyter notebook server on Lyceum Cloud.

    Starts a Jupyter notebook that you can access in your browser.
    The notebook URL will be printed once the server is ready.

    Examples:
        lyceum notebook launch
        lyceum notebook launch -m h100
        lyceum notebook launch -m a100 --timeout 7200
        lyceum notebook launch --image jupyter/scipy-notebook
    """
    status = StatusLine()

    try:
        config.get_client()

        status.start()
        status.update("Preparing notebook environment...")

        jupyter_image = image or JUPYTER_IMAGE

        # Build the Jupyter start command
        # Using start-notebook.sh with custom options
        jupyter_cmd = [
            "start-notebook.sh",
            f"--NotebookApp.token={token}",
            f"--port={port}",
            "--ip=0.0.0.0",
            "--no-browser",
        ]

        # Build request for v2 image API
        image_request = {
            "docker_image_ref": jupyter_image,
            "docker_run_cmd": jupyter_cmd,
            "timeout": timeout,
            "execution_type": machine_type,
        }

        status.update(f"Starting Jupyter on {machine_type}...")

        response = httpx.post(
            f"{config.base_url}/api/v2/external/execution/image/start",
            json=image_request,
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=30.0,
        )

        if response.status_code != 200:
            status.stop()
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            if response.status_code == 401:
                console.print(
                    "[red]Authentication failed. Your session may have expired.[/red]"
                )
                console.print("[yellow]Run 'lyceum auth login' to re-authenticate.[/yellow]")
            elif response.content:
                console.print(f"[red]{response.content.decode()}[/red]")
            raise typer.Exit(1)

        result = response.json()
        execution_id = result.get("execution_id")

        # Build the notebook URL immediately
        notebook_url = f"https://{execution_id}-{port}.port.lyceum.technology"
        full_url = f"{notebook_url}/?token={token}"

        status.stop()

        # Print URL immediately so user can click it
        console.print()
        console.print("[bold green]Notebook starting![/bold green]")
        console.print()
        console.print(f"[cyan]{full_url}[/cyan]")
        console.print()
        console.print(f"[dim]Execution ID:[/dim] {execution_id}")
        console.print()
        console.print("[dim]To stop:[/dim] lyceum notebook stop " + execution_id)

    except typer.Exit:
        status.stop()
        raise
    except Exception as e:
        status.stop()
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@notebook_app.command("stop")
def stop_notebook(
    execution_id: str = typer.Argument(..., help="Execution ID of the notebook to stop"),
):
    """Stop a running Jupyter notebook.

    Examples:
        lyceum notebook stop 9d73319c-6f1c-4b4c-90e4-044244353ce4
    """
    status = StatusLine()

    try:
        config.get_client()

        status.start()
        status.update("Stopping notebook...")

        response = httpx.post(
            f"{config.base_url}/api/v2/external/workloads/abort/{execution_id}",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=30.0,
        )

        status.stop()

        if response.status_code == 200:
            console.print(f"[green]Notebook {execution_id} stopped.[/green]")
        elif response.status_code == 404:
            console.print(f"[yellow]Notebook {execution_id} not found or already stopped.[/yellow]")
        else:
            console.print(f"[red]Error stopping notebook: HTTP {response.status_code}[/red]")
            if response.content:
                console.print(f"[red]{response.content.decode()}[/red]")
            raise typer.Exit(1)

    except typer.Exit:
        status.stop()
        raise
    except Exception as e:
        status.stop()
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@notebook_app.command("list")
def list_notebooks():
    """List running Jupyter notebooks.

    Shows all active notebook sessions with their URLs and status.
    """
    status = StatusLine()

    try:
        config.get_client()

        status.start()
        status.update("Fetching running notebooks...")

        # Use the workloads API to get running executions
        response = httpx.get(
            f"{config.base_url}/api/v2/external/workloads/list",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=30.0,
        )

        status.stop()

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            if response.content:
                console.print(f"[red]{response.content.decode()}[/red]")
            raise typer.Exit(1)

        executions = response.json()

        # Filter for notebook executions (those running on port 8888 or with jupyter)
        # Since we don't have image info, show all running executions
        notebooks = [
            e for e in executions
            if e.get("status") in ["running", "pending", "queued", "starting"]
        ]

        if not notebooks:
            console.print("[dim]No running workloads found.[/dim]")
            return

        console.print(f"[bold]Running Workloads ({len(notebooks)})[/bold]")
        console.print()

        for nb in notebooks:
            exec_id = nb.get("execution_id", "unknown")
            status_val = nb.get("status", "unknown")
            created = nb.get("created_at", "")
            file_name = nb.get("file_name", "")

            # Assume port 8888 for Jupyter
            url = f"https://{exec_id}-8888.port.lyceum.technology"

            console.print(f"[cyan]{exec_id}[/cyan]")
            if file_name:
                console.print(f"  Name: {file_name}")
            console.print(f"  Status: {status_val}")
            console.print(f"  URL: {url}")
            if created:
                console.print(f"  Created: {created}")
            console.print()

    except typer.Exit:
        raise
    except Exception as e:
        status.stop()
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


