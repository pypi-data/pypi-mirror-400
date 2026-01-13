"""
Docker execution commands
"""

import json
import shlex
from typing import Optional

import httpx
import typer
from rich.console import Console

from ....shared.config import config
from ....shared.streaming import StatusLine, stream_execution_output

console = Console()


docker_app = typer.Typer(name="docker", help="Docker execution commands")


@docker_app.command("run")
def run_docker(
    image: str = typer.Argument(..., help="Docker image to run"),
    machine_type: str = typer.Option(
        "cpu", "--machine", "-m", help="Machine type (cpu, a100, h100, etc.)"
    ),
    timeout: int = typer.Option(
        300, "--timeout", "-t", help="Execution timeout in seconds"
    ),
    file_name: Optional[str] = typer.Option(
        None, "--file-name", "-f", help="Name for the execution"
    ),
    command: Optional[str] = typer.Option(
        None,
        "--command",
        "-c",
        help="Command to run in container (e.g., 'python app.py')",
    ),
    env: Optional[list[str]] = typer.Option(
        None, "--env", "-e", help="Environment variables (e.g., KEY=value)"
    ),
    detach: bool = typer.Option(
        False, "--detach", "-d", help="Run container in background and print execution ID"
    ),
    callback_url: Optional[str] = typer.Option(
        None, "--callback", help="Webhook URL for completion notification"
    ),
    registry_creds: Optional[str] = typer.Option(
        None, "--registry-creds", help="Docker registry credentials as JSON string"
    ),
    registry_type: Optional[str] = typer.Option(
        None, "--registry-type", help="Registry credential type: basic, aws, etc."
    ),
):
    """Execute a Docker container on Lyceum Cloud.

    By default, streams container output in real-time.
    Use --detach to run in background and return immediately.

    Examples:
        lyceum docker run python:3.11 -c "python -c 'print(1+1)'"
        lyceum docker run myapp:latest -e "DEBUG=true"
        lyceum docker run nvidia/cuda:12.0-base -m a100 -d
    """
    status = StatusLine()

    try:
        config.get_client()

        status.start()
        status.update("Validating configuration...")

        # Parse environment variables
        docker_env = {}
        if env:
            for env_var in env:
                if "=" in env_var:
                    key, value = env_var.split("=", 1)
                    docker_env[key] = value
                else:
                    status.stop()
                    console.print(
                        f"[yellow]Warning: Ignoring invalid env var format: {env_var}[/yellow]"
                    )
                    status.start()

        # Parse registry credentials
        registry_credentials = None
        if registry_creds:
            try:
                registry_credentials = json.loads(registry_creds)
            except json.JSONDecodeError:
                status.stop()
                console.print(
                    "[red]Error: Invalid JSON format for registry credentials[/red]"
                )
                raise typer.Exit(1)

        # Validate registry credentials and type
        if (registry_creds and not registry_type) or (
            registry_type and not registry_creds
        ):
            status.stop()
            console.print(
                "[red]Error: Both --registry-creds and --registry-type must be provided together[/red]"
            )
            raise typer.Exit(1)

        status.update(f"Starting container {image}...")

        # Build request for v2 image API
        image_request = {
            "docker_image_ref": image,
            "timeout": timeout,
            "execution_type": machine_type,
        }

        if command:
            image_request["docker_run_cmd"] = shlex.split(command)
        if file_name:
            image_request["file_name"] = file_name
        if env:
            # Join with newlines - the execlet parses env vars by splitting on \n
            image_request["docker_run_env"] = "\n".join(env)

        # Handle registry credentials
        if registry_type and registry_credentials:
            image_request["docker_registry_credential_type"] = registry_type

            if registry_type == "aws":
                creds = registry_credentials
                image_request.update(
                    {
                        "aws_access_key_id": creds.get("aws_access_key_id"),
                        "aws_secret_access_key": creds.get("aws_secret_access_key"),
                        "aws_session_token": creds.get("aws_session_token"),
                        "aws_region": creds.get("region", "us-east-1"),
                    }
                )
            elif registry_type == "basic":
                creds = registry_credentials
                image_request.update(
                    {
                        "docker_username": creds.get("username"),
                        "docker_password": creds.get("password"),
                    }
                )

        # Call the v2 image endpoint
        status.update("Submitting execution...")

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
        streaming_url = result.get("streaming_url")

        if detach:
            # Detached mode - just return the execution info
            status.stop()
            console.print(f"[dim]Image: {image}[/dim]")
            console.print(f"[dim]Machine: {machine_type}[/dim]")
            console.print(f"[dim]Execution ID: {execution_id}[/dim]")
            console.print("")
            console.print(f"[dim]To stream logs:[/dim] lyceum docker logs {execution_id}")
        else:
            # Default: stream output in real-time (like docker run)
            success = stream_execution_output(execution_id, streaming_url, status)

            # Show execution ID at the end
            console.print(f"[dim]Execution ID: {execution_id}[/dim]")

            if not success:
                raise typer.Exit(1)

    except typer.Exit:
        status.stop()
        raise
    except Exception as e:
        status.stop()
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@docker_app.command("logs")
def docker_logs(
    execution_id: str = typer.Argument(..., help="Execution ID to stream logs from"),
):
    """Stream logs from a running or completed Docker execution.

    Examples:
        lyceum docker logs 9d73319c-6f1c-4b4c-90e4-044244353ce4
    """
    status = StatusLine()

    try:
        config.get_client()

        status.start()
        status.update("Connecting to execution...")

        # Pass None for streaming_url to use the default v2 endpoint
        success = stream_execution_output(execution_id, None, status)

        console.print(f"[dim]Execution ID: {execution_id}[/dim]")

        if not success:
            raise typer.Exit(1)

    except typer.Exit:
        status.stop()
        raise
    except Exception as e:
        status.stop()
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@docker_app.command("registry-examples")
def show_registry_examples():
    """Show examples of Docker registry credential formats"""
    console.print("[bold cyan]Docker Registry Credential Examples[/bold cyan]\n")

    console.print("[bold]1. Docker Hub (basic)[/bold]")
    console.print("Type: [green]basic[/green]")
    console.print(
        'Credentials: [yellow]\'{"username": "myuser", "password": "mypassword"}\'[/yellow]\n'
    )

    console.print("[bold]2. AWS ECR (aws)[/bold]")
    console.print("Type: [green]aws[/green]")
    console.print(
        'Credentials: [yellow]\'{"region": "us-west-2", "aws_access_key_id": "AKIAI...", "aws_secret_access_key": "wJalrX...", "session_token": "optional..."}\'[/yellow]\n'
    )

    console.print("[bold]3. Private Registry (basic)[/bold]")
    console.print("Type: [green]basic[/green]")
    console.print(
        'Credentials: [yellow]\'{"username": "admin", "password": "secret"}\'[/yellow]\n'
    )

    console.print("[bold]Example Commands:[/bold]")
    console.print("# Docker Hub:")
    console.print(
        "[dim]lyceum docker run myuser/myapp:latest --registry-type basic --registry-creds '{\"username\": \"myuser\", \"password\": \"mytoken\"}'[/dim]"
    )
    console.print("\n# AWS ECR:")
    console.print(
        "[dim]lyceum docker run 123456789012.dkr.ecr.us-west-2.amazonaws.com/myapp:latest --registry-type aws --registry-creds '{\"region\": \"us-west-2\", \"aws_access_key_id\": \"AKIAI...\", \"aws_secret_access_key\": \"wJalrX...\"}'[/dim]"
    )
    console.print("\n# Private Registry:")
    console.print(
        "[dim]lyceum docker run myregistry.com/myapp:latest --registry-type basic --registry-creds '{\"username\": \"admin\", \"password\": \"secret\"}'[/dim]"
    )
