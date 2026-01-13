"""Workspace configuration commands for Python execution"""

import importlib.metadata as im
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ....shared.imports import (
    is_stdlib_module_by_name,
    should_skip_path,
    find_imports_in_file,
    SKIP_DIRS,
)

console = Console()

config_app = typer.Typer(name="config", help="Workspace configuration commands")

# Known package name mismatches (import name -> pip name)
PACKAGE_NAME_MAP = {
    "sklearn": "scikit-learn",
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "bs4": "beautifulsoup4",
    "yaml": "PyYAML",
    "Crypto": "pycryptodome",
    "OpenSSL": "pyOpenSSL",
    "cudf": "cudf-cu12",
    "cpuinfo": "py-cpuinfo",
}


def get_package_name(module_name: str) -> str:
    """Convert import name to pip package name."""
    top_level = module_name.split(".")[0]
    return PACKAGE_NAME_MAP.get(top_level, top_level)


def get_installed_version(package_name: str) -> Optional[str]:
    """Get installed version of a package."""
    try:
        return im.version(package_name)
    except Exception:
        return None


def find_local_packages(workspace: Path) -> dict[str, Path]:
    """Find all local Python packages in the workspace recursively."""
    packages = {}

    for init_file in workspace.rglob("__init__.py"):
        if should_skip_path(init_file):
            continue

        package_dir = init_file.parent
        parent_init = package_dir.parent / "__init__.py"
        if parent_init.exists() and not should_skip_path(parent_init):
            continue

        try:
            rel_path = package_dir.relative_to(workspace)
            packages[str(rel_path)] = package_dir
        except ValueError:
            pass

    for item in workspace.iterdir():
        if should_skip_path(item):
            continue
        if item.is_file() and item.suffix == ".py" and item.stem != "__init__":
            packages[item.stem] = item

    return packages


def collect_all_python_files(workspace: Path) -> list[Path]:
    """Collect all Python files in the workspace."""
    py_files = []
    for py_file in workspace.rglob("*.py"):
        if not should_skip_path(py_file):
            py_files.append(py_file)
    return py_files


def parse_requirements_file(req_file: Path) -> list[str]:
    """Parse a requirements.txt file into a list of dependencies."""
    deps = []
    try:
        with open(req_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    deps.append(line)
    except Exception:
        pass
    return deps


def extract_package_name(dep: str) -> str:
    """Extract package name from a dependency string."""
    return dep.split("==")[0].split(">=")[0].split("<=")[0].split("<")[0].split(">")[0].split("[")[0].split("~=")[0].lower()


@config_app.command("init")
def init_config(
    workspace: Path = typer.Argument(".", help="Workspace directory to analyze"),
    requirements: Path | None = typer.Option(
        None, "--requirements", "-r", help="Path to requirements.txt"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
):
    """Initialize workspace configuration for Lyceum Cloud execution.

    Scans the workspace to detect:
    - Local Python packages (for import resolution at runtime)
    - External dependencies (from imports and requirements.txt)

    Creates .lyceum/config.json with workspace metadata.
    Local file contents are resolved at runtime based on what each script imports.

    Example:
        lyceum python config init
        lyceum python config init ./my-project
        lyceum python config init -r requirements.txt
    """
    workspace = Path(workspace).resolve()

    if not workspace.exists():
        console.print(f"[red]Error: Workspace directory does not exist: {workspace}[/red]")
        raise typer.Exit(1)

    config_dir = workspace / ".lyceum"
    config_file = config_dir / "config.json"

    if config_file.exists() and not force:
        console.print(f"[yellow]Config already exists: {config_file}[/yellow]")
        console.print("[dim]Use --force to overwrite[/dim]")
        raise typer.Exit(1)

    console.print(f"[dim]Scanning workspace: {workspace}[/dim]")

    # Find local packages
    local_packages = find_local_packages(workspace)
    console.print(f"[dim]Found {len(local_packages)} local packages/modules[/dim]")

    if local_packages:
        for name in sorted(local_packages.keys())[:10]:
            console.print(f"[dim]  - {name}[/dim]")
        if len(local_packages) > 10:
            console.print(f"[dim]  ... and {len(local_packages) - 10} more[/dim]")

    # Collect all Python files for import scanning
    py_files = collect_all_python_files(workspace)
    console.print(f"[dim]Found {len(py_files)} Python files[/dim]")

    # Scan all files for imports to detect external dependencies
    all_imports = set()
    for py_file in py_files:
        all_imports.update(find_imports_in_file(py_file))

    # Filter to external dependencies
    local_package_names = {Path(p).parts[0] if "/" in p else p for p in local_packages.keys()}
    external_deps = {
        imp for imp in all_imports
        if not is_stdlib_module_by_name(imp) and imp not in local_package_names
    }
    console.print(f"[dim]Found {len(external_deps)} external dependencies from imports[/dim]")

    # Parse requirements.txt
    requirements_deps = []
    req_file = requirements or workspace / "requirements.txt"
    if req_file.exists():
        console.print(f"[dim]Reading requirements from: {req_file}[/dim]")
        requirements_deps = parse_requirements_file(req_file)

    # Build merged dependencies with versions
    merged_deps = []
    req_names = {extract_package_name(dep) for dep in requirements_deps}

    for dep in requirements_deps:
        merged_deps.append(dep)

    for imp in sorted(external_deps):
        pkg_name = get_package_name(imp)
        if pkg_name.lower() not in req_names:
            version = get_installed_version(pkg_name)
            if version:
                merged_deps.append(f"{pkg_name}=={version}")
            else:
                merged_deps.append(pkg_name)

    # Build config (no local_imports - resolved at runtime)
    config_data = {
        "workspace": str(workspace),
        "local_packages": {name: str(path) for name, path in sorted(local_packages.items())},
        "dependencies": {
            "from_imports": sorted(external_deps),
            "from_requirements": requirements_deps,
            "merged": sorted(set(merged_deps), key=str.lower),
        },
    }

    # Write config
    config_dir.mkdir(exist_ok=True)
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)

    console.print(f"[green]Created config: {config_file}[/green]")
    console.print(f"[dim]  - {len(local_packages)} local packages[/dim]")
    console.print(f"[dim]  - {len(config_data['dependencies']['merged'])} dependencies[/dim]")
    console.print("[dim]  - Local imports resolved at runtime per-file[/dim]")


@config_app.command("show")
def show_config(
    workspace: Path = typer.Argument(".", help="Workspace directory"),
):
    """Show current workspace configuration."""
    workspace = Path(workspace).resolve()
    config_file = workspace / ".lyceum" / "config.json"

    if not config_file.exists():
        console.print(f"[yellow]No config found at: {config_file}[/yellow]")
        console.print("[dim]Run 'lyceum python config init' to create one[/dim]")
        raise typer.Exit(1)

    with open(config_file) as f:
        config_data = json.load(f)

    console.print(f"[bold]Workspace:[/bold] {config_data.get('workspace', 'unknown')}")

    local_packages = config_data.get("local_packages", {})
    console.print(f"\n[bold]Local packages ({len(local_packages)}):[/bold]")
    for pkg in list(local_packages.keys())[:15]:
        console.print(f"  - {pkg}")
    if len(local_packages) > 15:
        console.print(f"  ... and {len(local_packages) - 15} more")

    deps = config_data.get("dependencies", {})
    merged = deps.get("merged", [])
    console.print(f"\n[bold]Dependencies ({len(merged)}):[/bold]")
    for dep in merged[:20]:
        console.print(f"  - {dep}")
    if len(merged) > 20:
        console.print(f"  ... and {len(merged) - 20} more")


@config_app.command("refresh")
def refresh_config(
    workspace: Path = typer.Argument(".", help="Workspace directory"),
    requirements: Path | None = typer.Option(
        None, "--requirements", "-r", help="Path to requirements.txt"
    ),
):
    """Refresh workspace configuration (re-scans the workspace)."""
    init_config(workspace=workspace, requirements=requirements, force=True)
