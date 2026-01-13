"""Model discovery and information commands for AI inference"""


import httpx
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ....shared.config import config

console = Console()

models_app = typer.Typer(name="models", help="Model discovery and information")


@models_app.command("list")
def list_models(
    model_type: str | None = typer.Option(
        None, "--type", "-t", help="Filter by model type (text, image, multimodal, etc.)"
    ),
    available_only: bool = typer.Option(
        False, "--available", "-a", help="Show only available models"
    ),
    sync_only: bool = typer.Option(
        False, "--sync", help="Show only models that support synchronous inference"
    ),
    async_only: bool = typer.Option(
        False, "--async", help="Show only models that support async/batch inference"
    ),
):
    """List all available AI models"""
    try:
        # Determine the endpoint based on filters
        if sync_only:
            endpoint = "/api/v2/external/models/sync"
        elif async_only:
            endpoint = "/api/v2/external/models/async"
        elif model_type:
            endpoint = f"/api/v2/external/models/type/{model_type}"
        else:
            endpoint = "/api/v2/external/models/"

        url = f"{config.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {config.api_key}"}

        console.print("[dim]🔍 Fetching available models...[/dim]")

        with httpx.Client() as http_client:
            response = http_client.get(url, headers=headers, timeout=10.0)

            if response.status_code != 200:
                console.print(f"[red]❌ Error: HTTP {response.status_code}[/red]")
                console.print(f"[red]{response.text}[/red]")
                raise typer.Exit(1)

            models = response.json()

            # Filter by availability if requested
            if available_only:
                models = [m for m in models if m.get('available', False)]

            if not models:
                console.print("[yellow]⚠️  No models found matching your criteria[/yellow]")
                return

            # Create a detailed table
            table = Table(title="Available AI Models", show_header=True, header_style="bold cyan")
            table.add_column("Model ID", style="cyan", no_wrap=True)
            table.add_column("Name", style="white")
            table.add_column("Type", style="magenta")
            table.add_column("Provider", style="blue")
            table.add_column("Status", justify="center")
            table.add_column("Price/1K", justify="right", style="green")
            table.add_column("Sync", justify="center", style="yellow")
            table.add_column("Async", justify="center", style="yellow")

            # Sort models: available first, then by type, then by name
            sorted_models = sorted(models, key=lambda m: (
                not m.get('available', False),
                m.get('type', 'text'),
                m.get('model_id', '')
            ))

            for model in sorted_models:
                # Status with emoji
                status = "🟢 Yes" if model.get('available') else "🔴 No"

                # Sync/Async support
                sync_support = "✓" if model.get('supports_sync', True) else "✗"
                async_support = "✓" if model.get('supports_async', True) else "✗"

                # Price
                price = model.get('price_per_1k_tokens', 0)
                price_str = f"${price:.4f}" if price > 0 else "Free"

                table.add_row(
                    model.get('model_id', 'Unknown'),
                    model.get('name', 'Unknown'),
                    model.get('type', 'text').title(),
                    model.get('provider', 'unknown').title(),
                    status,
                    price_str,
                    sync_support,
                    async_support
                )

            console.print(table)

            # Show summary
            available_count = sum(1 for m in models if m.get('available'))
            total_count = len(models)
            console.print(f"\n[dim]📊 {available_count}/{total_count} models available[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@models_app.command("info")
def get_model_info(
    model_id: str = typer.Argument(..., help="Model ID to get information about"),
):
    """Get detailed information about a specific model"""
    try:
        url = f"{config.base_url}/api/v2/external/models/{model_id}"
        headers = {"Authorization": f"Bearer {config.api_key}"}

        console.print(f"[dim]🔍 Fetching info for model: {model_id}...[/dim]")

        with httpx.Client() as http_client:
            response = http_client.get(url, headers=headers, timeout=10.0)

            if response.status_code == 404:
                console.print(f"[red]❌ Model '{model_id}' not found[/red]")
                raise typer.Exit(1)
            elif response.status_code != 200:
                console.print(f"[red]❌ Error: HTTP {response.status_code}[/red]")
                console.print(f"[red]{response.text}[/red]")
                raise typer.Exit(1)

            model = response.json()

            # Build detailed info display
            status_color = "green" if model.get('available') else "red"
            status_text = "Available ✓" if model.get('available') else "Unavailable ✗"

            info_lines = [
                f"[bold cyan]Model ID:[/bold cyan] {model.get('model_id', 'Unknown')}",
                f"[bold]Name:[/bold] {model.get('name', 'Unknown')}",
                f"[bold]Description:[/bold] {model.get('description', 'No description available')}",
                "",
                f"[bold]Type:[/bold] {model.get('type', 'text').title()}",
                f"[bold]Provider:[/bold] {model.get('provider', 'unknown').title()}",
                f"[bold]Version:[/bold] {model.get('version', 'N/A')}",
                f"[bold]Status:[/bold] [{status_color}]{status_text}[/{status_color}]",
                "",
                "[bold yellow]Capabilities:[/bold yellow]",
                f"  • Synchronous inference: {'Yes ✓' if model.get('supports_sync', True) else 'No ✗'}",
                f"  • Asynchronous/Batch: {'Yes ✓' if model.get('supports_async', True) else 'No ✗'}",
                f"  • GPU Required: {'Yes' if model.get('gpu_required', False) else 'No'}",
                "",
                "[bold green]Input/Output:[/bold green]",
                f"  • Input types: {', '.join(model.get('input_types', []))}",
                f"  • Output types: {', '.join(model.get('output_types', []))}",
                f"  • Max input tokens: {model.get('max_input_tokens', 'N/A'):,}",
                f"  • Max output tokens: {model.get('max_output_tokens', 'N/A'):,}",
                "",
                "[bold green]Pricing:[/bold green]",
                f"  • Base price: ${model.get('price_per_1k_tokens', 0):.4f} per 1K tokens",
                f"  • Batch discount: {model.get('batch_pricing_discount', 0.5) * 100:.0f}% off",
                "",
                "[bold blue]Performance:[/bold blue]",
                f"  • Estimated latency: {model.get('estimated_latency_ms', 0):,} ms",
            ]

            panel = Panel(
                "\n".join(info_lines),
                title=f"[bold white]Model Information: {model.get('name', model_id)}[/bold white]",
                border_style="cyan",
                padding=(1, 2)
            )

            console.print(panel)

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@models_app.command("instances")
def list_model_instances(
    model_id: str = typer.Argument(..., help="Model ID to list instances for"),
):
    """List running instances for a specific model"""
    try:
        url = f"{config.base_url}/api/v2/external/models/{model_id}/instances"
        headers = {"Authorization": f"Bearer {config.api_key}"}

        console.print(f"[dim]🔍 Fetching instances for model: {model_id}...[/dim]")

        with httpx.Client() as http_client:
            response = http_client.get(url, headers=headers, timeout=10.0)

            if response.status_code == 404:
                console.print(f"[red]❌ Model '{model_id}' not found[/red]")
                raise typer.Exit(1)
            elif response.status_code != 200:
                console.print(f"[red]❌ Error: HTTP {response.status_code}[/red]")
                console.print(f"[red]{response.text}[/red]")
                raise typer.Exit(1)

            instances = response.json()

            if not instances:
                console.print(f"[yellow]⚠️  No instances found for model '{model_id}'[/yellow]")
                return

            # Create table for instances
            table = Table(title=f"Instances for {model_id}", show_header=True, header_style="bold cyan")
            table.add_column("Instance ID", style="cyan", no_wrap=True)
            table.add_column("Instance URL", style="blue")
            table.add_column("Status", justify="center", style="green")
            table.add_column("Node ID", style="magenta")
            table.add_column("Last Health Check", style="dim")

            for instance in instances:
                # Truncate instance ID for display
                instance_id = instance.get('id', 'Unknown')
                short_id = instance_id[:12] + "..." if len(instance_id) > 12 else instance_id

                status = instance.get('status', 'unknown')
                status_emoji = "🟢" if status == "running" else "🔴"

                table.add_row(
                    short_id,
                    instance.get('instance_url', 'N/A'),
                    f"{status_emoji} {status}",
                    instance.get('node_id', 'N/A') or 'N/A',
                    instance.get('last_health_check', 'N/A') or 'N/A'
                )

            console.print(table)
            console.print(f"\n[dim]📊 Total instances: {len(instances)}[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)
