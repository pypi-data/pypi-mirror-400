"""Register command for AG2 CLI - continuous agent heartbeat with AgentOS."""

from __future__ import annotations

import asyncio
import signal
from typing import Annotated, Any, Optional

import httpx
import typer
from rich.console import Console

from agentos.utils.heartbeat import heartbeat_loop, register_agent


console = Console()

# Create the main register command (not a group)
def register(
    a2a_server_url: Annotated[
        str,
        typer.Argument(help="URL to A2A server root"),
    ] = "http://localhost:8000",
    agentos_url: Annotated[
        str,
        typer.Option("--agentos-url", "-u", help="AgentOS API base URL"),
    ] = "https://api.ag2.ai/api/v1",
    interval: Annotated[
        int,
        typer.Option("--interval", "-i", help="Heartbeat interval in seconds"),
    ] = 30,
    name: Annotated[
        Optional[str],
        typer.Option("--name", "-n", help="Provider name (default: from agent card)"),
    ] = None,
    timeout: Annotated[
        float,
        typer.Option("--timeout", "-t", help="Request timeout in seconds"),
    ] = 10.0,
) -> None:
    """
    Register agent with AgentOS and continuously send heartbeats.

    This command:
    1. Fetches the agent card from the A2A server
    2. Registers with AgentOS by sending an initial heartbeat
    3. Continuously sends heartbeats at the specified interval

    The process runs until interrupted with Ctrl+C.
    """
    asyncio.run(
        _register_async(
            a2a_server_url=a2a_server_url,
            agentos_base_url=agentos_url,
            interval=interval,
            provider_name=name,
            timeout=timeout,
        )
    )


async def _register_async(
    a2a_server_url: str,
    agentos_base_url: str,
    interval: int,
    provider_name: Optional[str],
    timeout: float,
) -> None:
    """
    Async implementation of the register command.

    Args:
        a2a_server_url: URL to A2A server root
        agentos_base_url: AgentOS API base URL
        interval: Heartbeat interval in seconds
        provider_name: Optional provider name
        timeout: Request timeout in seconds
    """
    # Setup signal handling for graceful shutdown
    stop_event = asyncio.Event()

    def signal_handler(_sig: int, _frame: Any) -> None:  # type: ignore[misc]
        console.print("\n[yellow]Shutting down gracefully...[/yellow]")
        stop_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Fetch agent card and register
        console.print(f"[cyan]Fetching agent card from {a2a_server_url}...[/cyan]")

        agent_card, worker_id = await register_agent(
            a2a_server_url=a2a_server_url,
            agentos_base_url=agentos_base_url,
            provider_name=provider_name,
            console=console,
            worker_type="standalone",
        )

        final_name = provider_name or agent_card.get("name", "unknown")
        console.print(f"[green]✓ Registered '{final_name}' with AgentOS[/green]")
        console.print(f"[green]✓ Worker ID: {worker_id}[/green]")

        # Start heartbeat loop
        console.print(f"[cyan]Starting heartbeat (every {interval}s)...[/cyan]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")

        await heartbeat_loop(
            base_url=agentos_base_url,
            provider_name=final_name,
            endpoint_url=a2a_server_url,
            interval=interval,
            timeout=timeout,
            console=console,
            stop_event=stop_event,
            worker_type="standalone",
            worker_id=worker_id,
            agent_card=agent_card,
        )

    except httpx.HTTPError as e:
        console.print(f"[red]✗ HTTP Error: {e}[/red]")
        if hasattr(e, "response") and e.response is not None:
            console.print(f"[red]Response: {e.response.text}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)
    finally:
        console.print("[yellow]Stopped[/yellow]")
