"""Agent management commands for AG2 CLI."""

from __future__ import annotations

from datetime import datetime
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
    help="Manage agents",
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


class AgentDeploymentResponse(BaseModel):
    """Response model for a single agent deployment."""

    id: str
    agent_name: str
    agent_slug: str
    status: str
    docker_image_tag: str
    provider: str
    provider_app_name: str
    agent_card_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deployed_at: Optional[datetime] = None
    active_workers: Optional[list[WorkerMetadata]] = None


class PaginatedAgentDeploymentResponse(BaseModel):
    """Paginated response for agent deployments."""

    items: list[AgentDeploymentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@app.command(name="list")
def agents_list(
    status: Annotated[
        Optional[str],
        typer.Option("--status", "-s", help="Filter by status (e.g., deployed, failed)"),
    ] = None,
    page: Annotated[
        int,
        typer.Option("--page", "-p", help="Page number"),
    ] = 1,
    page_size: Annotated[
        int,
        typer.Option("--page-size", help="Number of items per page"),
    ] = 10,
    show_errors: Annotated[
        bool,
        typer.Option("--show-errors", help="Show only agents with errors"),
    ] = False,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (table, json)", show_default=True),
    ] = "table",
) -> None:
    """
    List all agent deployments.

    Displays a paginated table of agent deployments with their status,
    provider information, and deployment timestamps.
    """
    console.print("[cyan]Fetching agent deployments...[/cyan]\n")

    config = get_config()
    client = get_client(base_url=config.api_url)

    # Build query parameters
    params = {
        "page": page,
        "page_size": page_size,
    }
    if status:
        params["status"] = status

    try:
        response = client.get("/agents", params=params)

        # Parse response
        data = PaginatedAgentDeploymentResponse.model_validate(response.json())

        if not data.items:
            console.print("[yellow]No agents found[/yellow]")
            return
        if format == "json":
            import json

            console.print(json.dumps(response.json(), indent=2))
            return

        # Create table
        table = Table(title=f"Agent Deployments (Page {data.page}/{data.total_pages})")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Slug", style="blue")
        table.add_column("Status", style="bold")
        table.add_column("Provider", style="magenta")
        table.add_column("App Name", style="green")
        table.add_column("Deployed At", style="dim")

        # Add rows
        for agent in data.items:
            # Color-code status
            status_color = {
                "deployed": "green",
                "deploying": "yellow",
                "failed": "red",
                "pending": "blue",
            }.get(agent.status.lower(), "white")

            deployed_at = (
                agent.deployed_at.strftime("%Y-%m-%d %H:%M")
                if agent.deployed_at
                else "Not deployed"
            )

            table.add_row(
                agent.agent_name,
                agent.agent_slug,
                f"[{status_color}]{agent.status}[/{status_color}]",
                agent.provider,
                agent.provider_app_name,
                deployed_at,
            )

        console.print(table)

        # Print pagination info
        console.print(
            f"\n[dim]Showing {len(data.items)} of {data.total} total agents[/dim]"
        )

        # Show error messages if any failed agents
        if show_errors:
            failed_agents = [a for a in data.items if a.error_message]
            if failed_agents:
                console.print("\n[yellow]Agents with errors:[/yellow]")
                for agent in failed_agents:
                    console.print(f"  • [red]{agent.agent_name}[/red]: {agent.error_message}")

    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Failed to list agents (status {e.response.status_code})[/red]")
        console.print(f"[red]Error: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.RequestError as e:
        console.print(f"[red]✗ Request failed: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="get")
def agents_get(
    identifier: Annotated[
        str,
        typer.Argument(help="Agent ID or slug to retrieve"),
    ],
) -> None:
    """
    Get details of a specific agent deployment.

    The identifier can be either the agent's ID or slug.
    """
    console.print(f"[cyan]Fetching agent:[/cyan] {identifier}\n")

    config = get_config()
    client = get_client(base_url=config.api_url)

    try:
        response = client.get(f"/agents/{identifier}")

        # Parse response
        agent = AgentDeploymentResponse.model_validate(response.json())

        # Display agent details
        table = Table(title=f"Agent: {agent.agent_name}", show_header=True, header_style="bold cyan")
        table.add_column("Property", style="green")
        table.add_column("Value", style="white")

        # Add rows for each property
        table.add_row("ID", agent.id)
        table.add_row("Name", agent.agent_name)
        table.add_row("Slug", agent.agent_slug)

        # Color-code status
        status_color = {
            "deployed": "green",
            "deploying": "yellow",
            "failed": "red",
            "pending": "blue",
        }.get(agent.status.lower(), "white")
        table.add_row("Status", f"[{status_color}]{agent.status}[/{status_color}]")

        table.add_row("Docker Image Tag", agent.docker_image_tag)
        table.add_row("Provider", agent.provider)
        table.add_row("Provider App Name", agent.provider_app_name)

        if agent.agent_card_url:
            table.add_row("Agent Card URL", agent.agent_card_url)

        if agent.error_message:
            table.add_row("Error Message", f"[red]{agent.error_message}[/red]")

        table.add_row("Created At", agent.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        table.add_row("Updated At", agent.updated_at.strftime("%Y-%m-%d %H:%M:%S"))

        if agent.deployed_at:
            table.add_row("Deployed At", agent.deployed_at.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            table.add_row("Deployed At", "[dim]Not deployed[/dim]")

        console.print(table)

        # Display active workers if available
        if agent.active_workers:
            console.print(f"\n[cyan]Active Workers ({len(agent.active_workers)}):[/cyan]")
            workers_table = Table(show_header=True, header_style="bold cyan")
            workers_table.add_column("Worker ID", style="green")
            workers_table.add_column("Type", style="blue")
            workers_table.add_column("Endpoint URL", style="magenta")
            workers_table.add_column("Last Heartbeat", style="yellow")

            for worker in agent.active_workers:
                workers_table.add_row(
                    worker.worker_id,
                    worker.worker_type,
                    worker.endpoint_url,
                    worker.last_heartbeat,
                )

            console.print(workers_table)
        else:
            console.print("\n[dim]No active workers[/dim]")

    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Failed to get agent (status {e.response.status_code})[/red]")
        console.print(f"[red]Error: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.RequestError as e:
        console.print(f"[red]✗ Request failed: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="delete")
def agents_delete(
    identifier: Annotated[
        str,
        typer.Argument(help="Agent ID or slug to delete"),
    ],
    confirm: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
) -> None:
    """
    Delete an agent deployment.

    The identifier can be either the agent's ID or slug.
    """
    if not confirm:
        confirmed = typer.confirm(f"Are you sure you want to delete agent '{identifier}'?")
        if not confirmed:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)

    console.print(f"[cyan]Deleting agent:[/cyan] {identifier}")

    config = get_config()
    client = get_client(base_url=config.api_url)

    try:
        response = client.delete(f"/agents/{identifier}")

        console.print(f"[green]✓ Successfully deleted agent '{identifier}'[/green]")

        # Display response if available
        try:
            result = response.json()
            if result:
                console.print("\n[cyan]Server response:[/cyan]")
                import json
                console.print(json.dumps(result, indent=2))
        except Exception:
            pass

    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Failed to delete agent (status {e.response.status_code})[/red]")
        console.print(f"[red]Error: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.RequestError as e:
        console.print(f"[red]✗ Request failed: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


def output_logs(logs: str) -> None:
    """
    Output logs to console.

    Args:
        logs: Log content to display
    """
    console.print(logs, highlight=False, markup=False)


@app.command(name="logs")
def agents_logs(
    identifier: Annotated[
        str,
        typer.Argument(help="Agent ID or slug to get logs for"),
    ],
    lines: Annotated[
        int,
        typer.Option("--lines", "-n", help="Number of log lines to retrieve"),
    ] = 100,
    follow: Annotated[
        bool,
        typer.Option("--follow", "-f", help="Follow log output (stream logs)"),
    ] = False,
) -> None:
    """
    Get logs for a specific agent deployment.

    The identifier can be either the agent's ID or slug.

    Examples:
        ag2 agents logs my-agent              # Get last 100 lines
        ag2 agents logs my-agent --lines 500  # Get last 500 lines
        ag2 agents logs my-agent --follow     # Stream logs in real-time
    """
    config = get_config()
    client = get_client(base_url=config.api_url)

    if follow:
        console.print(f"[cyan]Following logs for agent:[/cyan] {identifier}")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")

        try:
            import time
            last_logs = ""

            while True:
                try:
                    params = {"lines": lines}
                    response = client.get(f"/agents/{identifier}/logs", params=params)
                    result = response.json()
                    logs = result.get("logs", "")

                    # Only print new logs
                    if logs != last_logs:
                        new_content = logs[len(last_logs):] if logs.startswith(last_logs) else logs
                        if new_content:
                            output_logs(new_content)
                        last_logs = logs

                    time.sleep(2)  # Poll every 2 seconds

                except KeyboardInterrupt:
                    console.print("\n[yellow]Stopped following logs[/yellow]")
                    break
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        console.print(f"[red]✗ Agent '{identifier}' not found[/red]")
                    else:
                        console.print(f"[red]✗ Failed to fetch logs (status {e.response.status_code})[/red]")
                        console.print(f"[red]Error: {e.response.text}[/red]")
                    break

        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            raise typer.Exit(1)
    else:
        console.print(f"[cyan]Fetching logs for agent:[/cyan] {identifier}")
        console.print(f"[dim]Showing last {lines} lines[/dim]\n")

        try:
            params = {"lines": lines}
            response = client.get(f"/agents/{identifier}/logs", params=params)
            result = response.json()
            logs = result.get("logs", "")

            if not logs:
                console.print("[yellow]No logs available[/yellow]")
                return

            output_logs(logs)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                console.print(f"[red]✗ Agent '{identifier}' not found[/red]")
            else:
                console.print(f"[red]✗ Failed to fetch logs (status {e.response.status_code})[/red]")
                console.print(f"[red]Error: {e.response.text}[/red]")
            raise typer.Exit(1)
        except httpx.RequestError as e:
            console.print(f"[red]✗ Request failed: {e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            raise typer.Exit(1)
