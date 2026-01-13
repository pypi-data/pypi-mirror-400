"""Secrets management commands for AG2 CLI."""

from __future__ import annotations

from typing import Annotated

import httpx
import typer
from rich.console import Console
from rich.table import Table

from agentos.client import get_client
from agentos.config import get_config

console = Console()
app = typer.Typer(
    help="Manage environment secrets",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command(name="create")
def secrets_create(
    key: Annotated[
        str,
        typer.Argument(help="Secret key name (e.g., OPENAI_API_KEY)"),
    ],
    value: Annotated[
        str,
        typer.Argument(help="Secret value"),
    ],
):
    """Create a new secret."""
    console.print(f"[cyan]Creating secret:[/cyan] {key}")

    config = get_config()
    client = get_client(base_url=config.api_url)

    payload = {"key": key, "value": value}

    try:
        response = client.post("/secrets", json=payload)
        console.print(f"[green]✓ Successfully created secret '{key}'[/green]")

        # Display response if available
        try:
            result = response.json()
            if result:
                console.print("\n[cyan]Server response:[/cyan]")
                console.print(result)
        except Exception:
            pass

    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Failed to create secret (status {e.response.status_code})[/red]")
        console.print(f"[red]Error: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.RequestError as e:
        console.print(f"[red]✗ Request failed: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="list")
def secrets_list():
    """List all secrets (only shows keys, not values)."""
    console.print("[cyan]Fetching secrets list...[/cyan]\n")

    config = get_config()
    client = get_client(base_url=config.api_url)

    try:
        response = client.get("/secrets")
        secrets = response.json()["secrets"]

        if not secrets:
            console.print("[yellow]No secrets found[/yellow]")
            return

        # Display as table
        table = Table(title="Secrets", show_header=True, header_style="bold cyan")
        table.add_column("Key", style="green")

        # Handle both list and dict responses
        if isinstance(secrets, list):
            for secret in secrets:
                if isinstance(secret, dict):
                    table.add_row(secret.get("key", str(secret)))
                else:
                    table.add_row(str(secret))
        elif isinstance(secrets, dict):
            for key in secrets.keys():
                table.add_row(key)

        console.print(table)

    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Failed to list secrets (status {e.response.status_code})[/red]")
        console.print(f"[red]Error: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.RequestError as e:
        console.print(f"[red]✗ Request failed: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="update")
def secrets_update(
    key: Annotated[
        str,
        typer.Argument(help="Secret key name to update"),
    ],
    value: Annotated[
        str,
        typer.Argument(help="New secret value"),
    ],
):
    """Update an existing secret."""
    console.print(f"[cyan]Updating secret:[/cyan] {key}")

    config = get_config()
    client = get_client(base_url=config.api_url)

    payload = {"value": value}

    try:
        response = client.put(f"/secrets/{key}", json=payload)
        console.print(f"[green]✓ Successfully updated secret '{key}'[/green]")

        # Display response if available
        try:
            result = response.json()
            if result:
                console.print("\n[cyan]Server response:[/cyan]")
                console.print(result)
        except Exception:
            pass

    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Failed to update secret (status {e.response.status_code})[/red]")
        console.print(f"[red]Error: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.RequestError as e:
        console.print(f"[red]✗ Request failed: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="delete")
def secrets_delete(
    key: Annotated[
        str,
        typer.Argument(help="Secret key name to delete"),
    ],
    confirm: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
):
    """Delete a secret."""
    if not confirm:
        confirmed = typer.confirm(f"Are you sure you want to delete secret '{key}'?")
        if not confirmed:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)

    console.print(f"[cyan]Deleting secret:[/cyan] {key}")

    config = get_config()
    client = get_client(base_url=config.api_url)

    try:
        response = client.delete(f"/secrets/{key}")
        console.print(f"[green]✓ Successfully deleted secret '{key}'[/green]")

        # Display response if available
        try:
            result = response.json()
            if result:
                console.print("\n[cyan]Server response:[/cyan]")
                console.print(result)
        except Exception:
            pass

    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Failed to delete secret (status {e.response.status_code})[/red]")
        console.print(f"[red]Error: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.RequestError as e:
        console.print(f"[red]✗ Request failed: {e}[/red]")
        raise typer.Exit(1)
