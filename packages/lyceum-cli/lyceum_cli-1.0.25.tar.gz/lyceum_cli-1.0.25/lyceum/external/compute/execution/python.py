"""Python execution commands"""

import json
import sys
from pathlib import Path

import httpx
import typer
from rich.console import Console

from ....shared.config import config
from ....shared.streaming import stream_execution_output, StatusLine
from ....shared.imports import DependencyResolver
from .config import config_app

console = Console()

python_app = typer.Typer(name="python", help="Python execution commands")

# Add config subcommand
python_app.add_typer(config_app, name="config")


def get_available_machines() -> list[str]:
    """Fetch available machine types for the current user."""
    try:
        response = httpx.get(
            f"{config.base_url}/api/v2/external/user/quotas/available-hardware",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("available_hardware_profiles", [])
    except Exception:
        pass
    return []


def validate_machine_type(machine_type: str) -> bool:
    """Validate that the user has access to the specified machine type."""
    available = get_available_machines()
    if not available:
        return True
    return machine_type in available


def load_workspace_config(file_path: Path | None = None) -> dict | None:
    """Load workspace config from .lyceum/config.json if it exists."""
    search_paths = []

    if file_path and file_path.exists():
        search_paths.append(file_path.parent.resolve())

    search_paths.append(Path.cwd().resolve())

    for start_path in search_paths:
        current = start_path
        while current != current.parent:
            config_file = current / ".lyceum" / "config.json"
            if config_file.exists():
                try:
                    with open(config_file, "r") as f:
                        data = json.load(f)
                        data["_config_dir"] = current
                        return data
                except Exception:
                    pass
            current = current.parent

    return None


def read_code_from_source(code_or_file: str, status: StatusLine = None) -> tuple[str, Path | None, str | None]:
    """Read code from file or return as-is if it's inline code."""
    file_path = Path(code_or_file) if Path(code_or_file).exists() else None

    if file_path:
        if status:
            status.update(f"Reading {file_path.name}...")
        with open(file_path) as f:
            code_content = f.read()
        return code_content, file_path, file_path.name

    return code_or_file, None, None


def inject_script_args(code: str, script_args: list[str], file_name: str | None) -> str:
    """Inject sys.argv setup at the beginning of the code if script args provided."""
    if not script_args:
        return code
    script_name = file_name or "script.py"
    argv_list = [script_name] + script_args
    argv_setup = f"import sys; sys.argv = {repr(argv_list)}\n"
    return argv_setup + code


def resolve_requirements(
    requirements: str | None,
    workspace_config: dict | None,
    debug: bool = False,
    status: StatusLine = None
) -> str | None:
    """Resolve requirements from explicit arg or workspace config."""
    if requirements:
        if Path(requirements).exists():
            if status:
                status.update("Loading requirements...")
            with open(requirements) as f:
                return f.read()
        else:
            return requirements

    if workspace_config:
        deps = workspace_config.get("dependencies", {})
        merged = deps.get("merged", [])
        if merged:
            if status:
                status.update(f"Loading {len(merged)} dependencies...")
            if debug:
                console.print("[cyan]DEBUG: Requirements to install:[/cyan]")
                for req in merged[:10]:
                    console.print(f"[cyan]  - {req}[/cyan]")
                if len(merged) > 10:
                    console.print(f"[cyan]  ... and {len(merged) - 10} more[/cyan]")
            return "\n".join(merged)

    return None


def resolve_import_files(
    file_path: Path | None,
    workspace_config: dict | None,
    debug: bool = False,
    status: StatusLine = None
) -> str | None:
    """Resolve local import files by analyzing the target file's imports at runtime."""
    if not file_path or not file_path.exists():
        return None

    if status:
        status.update("Resolving imports...")

    # Determine project root from workspace config or file's directory
    if workspace_config and "_config_dir" in workspace_config:
        project_root = workspace_config["_config_dir"]
    else:
        project_root = file_path.parent

    # Add project root to sys.path for import resolution
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)

    file_dir_str = str(file_path.parent)
    if file_dir_str not in sys.path:
        sys.path.insert(0, file_dir_str)

    # Resolve imports from the target file
    resolver = DependencyResolver(project_root)
    resolved_file_path = file_path.resolve()
    resolver.find_imports(resolved_file_path, resolved_file_path)

    # Exclude the main file itself
    local_files = {p for p in resolver.local_imports if p != file_path.resolve()}

    if not local_files:
        return None

    # Build import_files dict
    import_files_dict = {}
    for dep in sorted(local_files):
        if dep in resolver.import_path_map:
            rel_path = resolver.import_path_map[dep]
        else:
            try:
                rel_path = str(dep.relative_to(file_path.parent))
            except ValueError:
                try:
                    rel_path = str(dep.relative_to(project_root))
                except ValueError:
                    rel_path = str(dep)

        try:
            with open(dep, "r", encoding="utf-8") as f:
                import_files_dict[rel_path] = f.read()
        except Exception:
            pass

    if not import_files_dict:
        return None

    if debug:
        console.print("[cyan]DEBUG: Local files to include:[/cyan]")
        for rel_path in sorted(import_files_dict.keys())[:20]:
            code_len = len(import_files_dict[rel_path])
            console.print(f"[cyan]  - {rel_path} ({code_len} chars)[/cyan]")
        if len(import_files_dict) > 20:
            console.print(f"[cyan]  ... and {len(import_files_dict) - 20} more files[/cyan]")

    return json.dumps(import_files_dict)


def build_payload(
    code: str,
    machine_type: str,
    file_name: str | None = None,
    requirements_content: str | None = None,
    imports: list[str] | None = None,
    import_files: str | None = None,
) -> dict:
    """Build the execution request payload."""
    payload = {
        "code": code,
        "nbcode": 0,
        "execution_type": machine_type,
        "timeout": 60,
    }

    if file_name:
        payload["file_name"] = file_name
    if requirements_content:
        payload["requirements_content"] = requirements_content
    if imports:
        payload["prior_imports"] = imports
    if import_files:
        payload["import_files"] = import_files

    return payload


def log_payload_debug(payload: dict) -> None:
    """Log payload summary for debugging."""
    console.print("[cyan]DEBUG: Payload summary:[/cyan]")
    console.print(f"[cyan]  - execution_type: {payload.get('execution_type')}[/cyan]")
    console.print(f"[cyan]  - file_name: {payload.get('file_name')}[/cyan]")
    console.print(f"[cyan]  - code length: {len(payload.get('code', ''))} chars[/cyan]")
    console.print(f"[cyan]  - requirements_content: {len(payload.get('requirements_content', '') or '')} chars[/cyan]")
    console.print(f"[cyan]  - import_files: {len(payload.get('import_files', '') or '')} chars[/cyan]")


def submit_execution(payload: dict, status: StatusLine = None) -> tuple[str, str | None]:
    """Submit execution request to API."""
    if status:
        status.update("Submitting execution...")

    response = httpx.post(
        f"{config.base_url}/api/v2/external/execution/streaming/start",
        headers={"Authorization": f"Bearer {config.api_key}"},
        json=payload,
        timeout=30.0
    )

    if response.status_code != 200:
        if status:
            status.stop()
        console.print(f"[red]Error: HTTP {response.status_code}[/red]")
        if response.status_code == 401:
            console.print("[red]Authentication failed. Your session may have expired.[/red]")
            console.print("[yellow]Run 'lyceum auth login' to re-authenticate.[/yellow]")
        else:
            console.print(f"[red]{response.content.decode()}[/red]")
        raise typer.Exit(1)

    data = response.json()
    execution_id = data['execution_id']
    streaming_url = data.get('streaming_url')

    return execution_id, streaming_url


@python_app.command("run", context_settings={"allow_extra_args": True, "allow_interspersed_args": True})
def run_python(
    ctx: typer.Context,
    code_or_file: str = typer.Argument(..., help="Python code to execute or path to Python file"),
    machine_type: str = typer.Option(
        "cpu", "--machine", "-m", help="Machine type (cpu, a100, h100, etc.)"
    ),
    file_name: str | None = typer.Option(None, "--file-name", "-f", help="Name for the execution"),
    requirements: str | None = typer.Option(
        None, "--requirements", "-r", help="Requirements file path or pip requirements string"
    ),
    imports: list[str] | None = typer.Option(
        None, "--import", help="Pre-import modules (can be used multiple times)"
    ),
    use_config: bool = typer.Option(
        True, "--use-config/--no-config",
        help="Use workspace config from .lyceum/config.json if available"
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d",
        help="Show detailed debug information about config, requirements, and payload"
    ),
):
    """Execute Python code or file on Lyceum Cloud.

    If a .lyceum/config.json exists in the workspace (created by 'lyceum python config init'),
    requirements will be automatically loaded from it.
    Local imports are resolved at runtime from the target file.

    Script arguments can be passed after the file path:

        lyceum python run train.py -- --epochs 10 --lr 0.001
        lyceum python run script.py -- arg1 arg2 --flag value
    """
    status = StatusLine()

    try:
        config.get_client()

        if not validate_machine_type(machine_type):
            available = get_available_machines()
            console.print(f"[red]Error: You don't have access to machine type '{machine_type}'[/red]")
            if available:
                console.print(f"[dim]Available machines: {', '.join(available)}[/dim]")
            console.print("[dim]Run 'lyceum python machines' to see available machine types.[/dim]")
            raise typer.Exit(1)

        status.start()
        script_args = [arg for arg in (ctx.args or []) if arg != '--']

        code, file_path, detected_file_name = read_code_from_source(code_or_file, status)
        if not file_name:
            file_name = detected_file_name

        code = inject_script_args(code, script_args, file_name)

        workspace_config = None
        if use_config:
            status.update("Loading workspace config...")
            workspace_config = load_workspace_config(file_path)
            if workspace_config and debug:
                status.stop()
                console.print(f"[cyan]DEBUG: Config keys: {list(workspace_config.keys())}[/cyan]")
                status.start()

        requirements_content = resolve_requirements(requirements, workspace_config, debug, status)
        import_files = resolve_import_files(file_path, workspace_config, debug, status)

        payload = build_payload(
            code=code,
            machine_type=machine_type,
            file_name=file_name,
            requirements_content=requirements_content,
            imports=imports,
            import_files=import_files,
        )

        if debug:
            status.stop()
            log_payload_debug(payload)
            status.start()

        execution_id, streaming_url = submit_execution(payload, status)

        success = stream_execution_output(execution_id, streaming_url, status)

        # Show execution ID at the end
        console.print(f"[dim]Execution ID: {execution_id}[/dim]")

        if not success:
            console.print("[yellow]You can check the execution later with: lyceum status[/yellow]")
            raise typer.Exit(1)

    except typer.Exit:
        status.stop()
        raise
    except Exception as e:
        status.stop()
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
