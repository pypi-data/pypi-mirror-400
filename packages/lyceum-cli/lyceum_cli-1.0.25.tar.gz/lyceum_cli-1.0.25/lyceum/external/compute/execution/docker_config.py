"""Docker registry configuration commands"""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()

docker_config_app = typer.Typer(name="config", help="Docker registry configuration")

CONFIG_DIR = Path.home() / ".lyceum"
DOCKER_CONFIG_FILE = CONFIG_DIR / "docker-registries.json"


def load_docker_config() -> dict:
    """Load docker registry configuration."""
    if DOCKER_CONFIG_FILE.exists():
        try:
            with open(DOCKER_CONFIG_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"registries": {}}


def save_docker_config(config: dict) -> None:
    """Save docker registry configuration."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(DOCKER_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    # Set restrictive permissions since this contains credentials
    DOCKER_CONFIG_FILE.chmod(0o600)


def get_hub_credentials(image: str) -> dict | None:
    """Get Docker Hub credentials if the image is from Docker Hub.

    Docker Hub images either have no registry prefix or use docker.io.
    Returns None if no credentials found or image is not from Docker Hub.
    """
    config = load_docker_config()
    registries = config.get("registries", {})

    if "hub" not in registries:
        return None

    # Check if this looks like a Docker Hub image
    # Docker Hub: no dots in the first part, or explicitly docker.io
    if "/" not in image:
        # Single name like "python:3.9" - it's Docker Hub
        return registries["hub"]

    parts = image.split("/")
    first_part = parts[0]

    # If first part has a dot, it's a custom registry (not Docker Hub)
    # Exception: docker.io is Docker Hub
    if "." in first_part and first_part != "docker.io":
        return None

    # Otherwise it's Docker Hub (e.g., "myuser/myimage" or "docker.io/myuser/myimage")
    return registries["hub"]


@docker_config_app.command("hub")
def configure_hub():
    """Configure Docker Hub credentials interactively."""
    console.print("\n[bold]Docker Hub Configuration[/bold]")
    console.print("[dim]These credentials will be used for private Docker Hub images.[/dim]\n")

    username = typer.prompt("Docker Hub Username")
    password = typer.prompt("Docker Hub Password/Token", hide_input=True)

    config = load_docker_config()
    config["registries"]["hub"] = {
        "username": username,
        "password": password,
    }
    save_docker_config(config)

    console.print("\n[green]Docker Hub credentials saved![/green]")
    console.print("[dim]Credentials stored in ~/.lyceum/docker-registries.json[/dim]")


@docker_config_app.command("show")
def show_config():
    """Show configured docker registries."""
    config = load_docker_config()
    registries = config.get("registries", {})

    if not registries:
        console.print("[dim]No docker registries configured.[/dim]")
        console.print("[dim]Run 'lyceum docker config hub' to configure Docker Hub.[/dim]")
        console.print("[dim]For AWS ECR, use 'lyceum docker run <image> --aws' to auto-detect credentials.[/dim]")
        return

    table = Table(title="Configured Docker Registries")
    table.add_column("Registry", style="cyan")
    table.add_column("Details", style="dim")

    if "hub" in registries:
        hub = registries["hub"]
        username = hub.get("username", "")
        table.add_row("Docker Hub", f"User: {username}")

    console.print(table)
    console.print("\n[dim]For AWS ECR, use 'lyceum docker run <image> --aws' to auto-detect credentials.[/dim]")


@docker_config_app.command("clear")
def clear_config():
    """Clear saved Docker Hub credentials."""
    config = load_docker_config()

    if "hub" in config.get("registries", {}):
        del config["registries"]["hub"]
        save_docker_config(config)
        console.print("[green]Cleared Docker Hub credentials.[/green]")
    else:
        console.print("[yellow]No Docker Hub credentials found.[/yellow]")
