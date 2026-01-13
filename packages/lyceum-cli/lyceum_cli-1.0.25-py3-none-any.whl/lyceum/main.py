#!/usr/bin/env python3
"""
Lyceum CLI - Command-line interface for Lyceum Cloud Execution API
Refactored to match API directory structure
"""

import typer
from rich.console import Console

# Import all command modules
from .external.auth.login import auth_app
from .external.compute.execution.python import python_app
from .external.compute.execution.docker import docker_app
from .external.compute.execution.workloads import workloads_app
from .external.compute.execution.notebook import notebook_app

app = typer.Typer(
    name="lyceum",
    help="Lyceum Cloud Execution CLI",
    add_completion=False,
)

console = Console()

# Add all command groups
app.add_typer(auth_app, name="auth")
app.add_typer(python_app, name="python")
app.add_typer(docker_app, name="docker")
app.add_typer(workloads_app, name="workloads")
app.add_typer(notebook_app, name="notebook")

















if __name__ == "__main__":
    app()
