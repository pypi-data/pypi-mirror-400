"""Worker management commands for AG2 CLI."""

from __future__ import annotations

from typing import Annotated, Optional

import httpx
import typer
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

from agentos.client import get_client
from agentos.config import get_config

console = Console()
app = typer.Typer(
    help="Manage workers",
    context_settings={"help_option_names": ["-h", "--help"]},
)


class WorkerMetadata(BaseModel):
    """Metadata for an active worker."""

    worker_id: str
    worker_type: str
    endpoint_url: str
    last_heartbeat: str
    agent_slug: Optional[str] = None
    deployment_id: Optional[str] = None


class AllWorkersResponse(BaseModel):
    """Response model for all workers."""

    workers: list[WorkerMetadata]
    count: int


@app.command(name="list")
def workers_list(
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format (table, json)",
            case_sensitive=False,
        ),
    ] = "table",
) -> None:
    """
    List all active workers.

    Displays all workers (provisioned and standalone) as a flat list
    with their metadata including worker ID, type, endpoint, and last heartbeat.
    """
    console.print("[cyan]Fetching active workers...[/cyan]\n")

    config = get_config()
    client = get_client(base_url=config.api_url)

    try:
        response = client.get("/workers")

        # Parse response
        data = AllWorkersResponse.model_validate(response.json())

        if not data.workers:
            console.print("[yellow]No active workers found[/yellow]")
            return
        if format.lower() == "json":
            console.print_json(response.text)
            return

        # Create table
        table = Table(title=f"Active Workers (Total: {data.count})", show_header=True, header_style="bold cyan")
        table.add_column("Worker ID", style="green")
        table.add_column("Type", style="blue")
        table.add_column("Agent Slug", style="cyan")
        table.add_column("Endpoint URL", style="magenta")
        table.add_column("Last Heartbeat", style="yellow")
        table.add_column("Deployment ID", style="dim")

        # Add rows
        for worker in data.workers:
            table.add_row(
                worker.worker_id,
                worker.worker_type,
                worker.agent_slug or "[dim]N/A[/dim]",
                worker.endpoint_url,
                worker.last_heartbeat,
                worker.deployment_id or "[dim]N/A[/dim]",
            )

        console.print(table)
        console.print(f"\n[dim]Total: {data.count} active workers[/dim]")

    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Failed to list workers (status {e.response.status_code})[/red]")
        console.print(f"[red]Error: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.RequestError as e:
        console.print(f"[red]✗ Request failed: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)
