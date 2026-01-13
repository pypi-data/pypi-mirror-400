"""Deployment commands for AG2 CLI."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Annotated
import zipfile
import tempfile

import httpx
import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from agentos.config import get_config

console = Console()
app = typer.Typer(
    help="Deployment commands",
    context_settings={"help_option_names": ["-h", "--help"]},
)

def _zip_agent_directory(agent_path: Path, output_path: Path) -> Path:
    zip_path = output_path / f"{agent_path.name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in agent_path.rglob("*"):
            zipf.write(file, file.relative_to(agent_path))
    return zip_path

@app.command(name="create")
def deploy_create(
    path: Annotated[
        str,
        typer.Argument(help="Path to agent directory"),
    ],
    dockerfile: Annotated[
        str | None,
        typer.Option("--dockerfile", "-f", help="Custom Dockerfile path"),
    ] = None,
    agent_name: Annotated[
        str | None,
        typer.Option("--name", "-n", help="Agent name"),
    ] = None,
):
    """Deploy an agent by uploading a zip bundle to the AG2 server."""
    agent_path = Path(path)

    if not agent_path.exists():
        console.print(f"[red]Error: Agent path '{agent_path}' does not exist[/red]")
        raise typer.Exit(1)

    # Determine dockerfile path (relative to agent directory)
    if dockerfile:
        dockerfile_path = Path(dockerfile)
    else:
        dockerfile_path = agent_path / "Dockerfile"

    if not dockerfile_path.exists():
        console.print(f"[red]Error: Dockerfile not found at '{dockerfile_path}'[/red]")
        raise typer.Exit(1)

    # Use relative path for dockerfile_path in the upload
    relative_dockerfile = dockerfile_path.relative_to(agent_path) if dockerfile_path.is_relative_to(agent_path) else Path("Dockerfile")

    # Determine agent name
    final_agent_name = agent_name or agent_path.name

    console.print(f"[cyan]Preparing to deploy agent:[/cyan] {final_agent_name}")
    console.print(f"[cyan]Agent path:[/cyan] {agent_path}")
    console.print(f"[cyan]Dockerfile:[/cyan] {relative_dockerfile}")

    # Create temporary directory and zip the agent
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        console.print("\n[yellow]Creating agent bundle...[/yellow]")
        zip_path = _zip_agent_directory(agent_path, temp_path)
        console.print(f"[green]✓[/green] Created bundle: {zip_path}")

        # Prepare multipart upload
        config = get_config()
        console.print(f"\n[yellow]Uploading to {config.api_url}/agents/upload...[/yellow]")

        # Use longer timeout for file upload
        from agentos.client import AG2Client
        client = AG2Client(base_url=config.api_url, timeout=30.0)

        with open(zip_path, "rb") as zip_file:
            files = {
                "code_bundle": (zip_path.name, zip_file, "application/zip")
            }
            data = {
                "agent_name": final_agent_name,
                "dockerfile_path": str(relative_dockerfile),
                "resources": json.dumps({}),
                "env_vars": json.dumps([])
            }

            try:
                response = client.upload_file(
                    "/agents/upload",
                    files=files,
                    data=data
                )

                console.print(f"[green]✓ Successfully deployed agent '{final_agent_name}'[/green]")

                # Display response if available
                try:
                    result = response.json()
                    console.print("\n[cyan]Server response:[/cyan]")
                    console.print(result)
                except Exception:
                    console.print(f"\n[dim]Response: {response.text}[/dim]")

            except httpx.HTTPStatusError as e:
                console.print(f"[red]✗ Upload failed with status {e.response.status_code}[/red]")
                console.print(f"[red]Error: {e.response.text}[/red]")
                raise typer.Exit(1)
            except httpx.RequestError as e:
                console.print(f"[red]✗ Upload failed: {e}[/red]")
                raise typer.Exit(1)