"""API key management commands for AG2 CLI."""

from __future__ import annotations

from typing import Annotated

import httpx
import typer
from rich.console import Console
from rich.table import Table

from agentos.client import AG2Client, get_client
from agentos.config import get_config

console = Console()
app = typer.Typer(
    help="Manage API keys for authentication",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def callback():
    """API key management (primarily for workers)."""
    console.print(
        "[yellow]Note: API key commands are primarily for worker authentication. "
        "For CLI authentication, use 'ag2 login'.[/yellow]\n"
    )


@app.command(name="bootstrap")
def api_key_bootstrap(
    organization_id: Annotated[
        str,
        typer.Argument(help="Organization ID to bootstrap"),
    ],
    bootstrap_secret: Annotated[
        str,
        typer.Option(
            "--secret",
            "-s",
            help="Bootstrap secret (or set AG2_BOOTSTRAP_SECRET env var)",
            envvar="AG2_BOOTSTRAP_SECRET",
        ),
    ],
):
    """
    Bootstrap first API key for an organization.

    This is a one-time operation to create the initial client API key.
    Requires the BOOTSTRAP_SECRET configured on the server.

    Example:
        ag2 api-keys bootstrap my-org --secret <bootstrap-secret>
    """
    if not bootstrap_secret:
        console.print("[red]✗ Bootstrap secret is required[/red]")
        console.print("[yellow]Provide via --secret flag or AG2_BOOTSTRAP_SECRET env var[/yellow]")
        raise typer.Exit(1)

    config = get_config()
    console.print(f"[cyan]Bootstrapping API key for organization:[/cyan] {organization_id}")

    # Create client without API key for bootstrap
    client = AG2Client(base_url=config.api_url, api_key=None)

    try:
        response = client.post(
            "/api-keys/bootstrap",
            params={
                "organization_id": organization_id,
                "bootstrap_secret": bootstrap_secret,
            },
        )

        result = response.json()
        api_key = result["key"]
        key_type = result["key_type"]
        created_at = result["created_at"]

        console.print(f"[green]✓ Successfully created {key_type} API key[/green]\n")

        # Display the API key (only shown once!)
        console.print("[bold red]⚠️  IMPORTANT: Save this API key - it will not be shown again![/bold red]\n")
        console.print(f"[bold cyan]API Key:[/bold cyan] {api_key}")
        console.print(f"[cyan]Organization ID:[/cyan] {organization_id}")
        console.print(f"[cyan]Created:[/cyan] {created_at}\n")

        # Store credentials
        AG2Client.store_api_key(api_key)
        AG2Client.store_organization_id(organization_id)

        console.print("[green]✓ API key and organization ID stored securely[/green]")

    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Failed to bootstrap API key (status {e.response.status_code})[/red]")
        console.print(f"[red]Error: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.RequestError as e:
        console.print(f"[red]✗ Request failed: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="create")
def api_key_create(
    key_type: Annotated[
        str,
        typer.Argument(help="Key type: 'client' or 'agent'"),
    ] = "client",
):
    """
    Create a new API key (requires existing authentication).

    Key types:
    - client: For CLI and client applications
    - agent: For agent-to-agent communication

    Example:
        ag2 api-keys create client
    """
    if key_type not in ["client", "agent"]:
        console.print("[red]✗ Invalid key type. Must be 'client' or 'agent'[/red]")
        raise typer.Exit(1)

    config = get_config()
    client = get_client(base_url=config.api_url)

    if not client.api_key:
        console.print("[red]✗ No API key found. Please run 'ag2 api-keys bootstrap' first[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Creating {key_type} API key...[/cyan]")

    try:
        response = client.post(
            "/api-keys",
            json={"key_type": key_type},
        )

        result = response.json()
        api_key = result["key"]
        created_at = result["created_at"]

        console.print(f"[green]✓ Successfully created {key_type} API key[/green]\n")

        # Display the API key (only shown once!)
        console.print("[bold red]⚠️  IMPORTANT: Save this API key - it will not be shown again![/bold red]\n")
        console.print(f"[bold cyan]API Key:[/bold cyan] {api_key}")
        console.print(f"[cyan]Type:[/cyan] {key_type}")
        console.print(f"[cyan]Created:[/cyan] {created_at}\n")

    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Failed to create API key (status {e.response.status_code})[/red]")
        console.print(f"[red]Error: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.RequestError as e:
        console.print(f"[red]✗ Request failed: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="list")
def api_key_list():
    """
    List all API keys for your organization.

    Shows key metadata but not the actual key values.
    """
    config = get_config()
    client = get_client(base_url=config.api_url)

    if not client.api_key:
        console.print("[red]✗ No API key found. Please run 'ag2 api-keys bootstrap' first[/red]")
        raise typer.Exit(1)

    console.print("[cyan]Fetching API keys...[/cyan]\n")

    try:
        response = client.get("/api-keys")
        result = response.json()

        keys = result["keys"]
        count = result["count"]

        if count == 0:
            console.print("[yellow]No API keys found[/yellow]")
            return

        # Display as table
        table = Table(title=f"API Keys ({count})", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="dim")
        table.add_column("Type", style="green")
        table.add_column("Key Suffix", style="yellow")
        table.add_column("Created", style="cyan")
        table.add_column("Last Used", style="magenta")

        for key in keys:
            last_used = key.get("last_used_at") or "Never"
            table.add_row(
                key["id"],
                key["key_type"],
                key["key_suffix"],
                key["created_at"],
                last_used,
            )

        console.print(table)

    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Failed to list API keys (status {e.response.status_code})[/red]")
        console.print(f"[red]Error: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.RequestError as e:
        console.print(f"[red]✗ Request failed: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="delete")
def api_key_delete(
    key_id: Annotated[
        str,
        typer.Argument(help="API key ID to delete"),
    ],
    confirm: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
):
    """
    Delete an API key.

    Example:
        ag2 api-keys delete key_abc123
    """
    config = get_config()
    client = get_client(base_url=config.api_url)

    if not client.api_key:
        console.print("[red]✗ No API key found. Please run 'ag2 api-keys bootstrap' first[/red]")
        raise typer.Exit(1)

    if not confirm:
        confirmed = typer.confirm(f"Are you sure you want to delete API key '{key_id}'?")
        if not confirmed:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)

    console.print(f"[cyan]Deleting API key:[/cyan] {key_id}")

    try:
        response = client.delete(f"/api-keys/{key_id}")
        result = response.json()

        console.print(f"[green]✓ {result['message']}[/green]")

    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Failed to delete API key (status {e.response.status_code})[/red]")
        console.print(f"[red]Error: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.RequestError as e:
        console.print(f"[red]✗ Request failed: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="set")
def api_key_set(
    api_key: Annotated[
        str,
        typer.Argument(help="API key to store"),
    ],
    organization_id: Annotated[
        str,
        typer.Option("--org-id", "-o", help="Organization ID"),
    ],
):
    """
    Manually set API key and organization ID.

    Use this if you already have an API key and want to configure the CLI.

    Example:
        ag2 api-keys set <your-api-key> --org-id <your-org-id>
    """
    AG2Client.store_api_key(api_key)
    AG2Client.store_organization_id(organization_id)

    console.print("[green]✓ API key and organization ID stored securely[/green]")
    console.print(f"[cyan]Organization ID:[/cyan] {organization_id}")


@app.command(name="clear")
def api_key_clear(
    confirm: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
):
    """
    Clear stored API key and organization ID.

    This removes credentials from the system keyring.
    """
    if not confirm:
        confirmed = typer.confirm("Are you sure you want to clear stored credentials?")
        if not confirmed:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)

    AG2Client.clear_credentials()
    console.print("[green]✓ Credentials cleared[/green]")


@app.command(name="show")
def api_key_show():
    """
    Show currently stored credentials (masked for security).
    """
    api_key = AG2Client.get_stored_api_key()
    org_id = AG2Client.get_stored_organization_id()

    if not api_key and not org_id:
        console.print("[yellow]No credentials stored[/yellow]")
        console.print("[cyan]Run 'ag2 api-keys bootstrap' to get started[/cyan]")
        return

    console.print("[cyan]Stored Credentials:[/cyan]\n")

    if api_key:
        # Show only last 8 characters
        masked_key = "*" * (len(api_key) - 8) + api_key[-8:] if len(api_key) > 8 else "***"
        console.print(f"[cyan]API Key:[/cyan] {masked_key}")
    else:
        console.print("[cyan]API Key:[/cyan] [dim]Not set[/dim]")

    if org_id:
        console.print(f"[cyan]Organization ID:[/cyan] {org_id}")
    else:
        console.print("[cyan]Organization ID:[/cyan] [dim]Not set[/dim]")
