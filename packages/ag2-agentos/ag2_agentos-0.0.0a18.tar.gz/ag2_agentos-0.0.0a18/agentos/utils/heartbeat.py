"""Heartbeat and registration utilities for AG2 agents with AgentOS."""

from __future__ import annotations

import asyncio
import contextlib
from typing import Any, Optional

import httpx
from rich.console import Console

from agentos.config import get_config
from agentos.client import get_client_from_config


def heartbeat_agentos(
    base_url: str,
    provider_name: str,
    endpoint_url: str,
    timeout: float = 10.0,
    console: Optional[Console] = None,
    worker_type: Optional[str] = None,
    worker_id: Optional[str] = None,
    agent_card: Optional[dict[str, Any]] = None,
    worker_api_key: Optional[str] = None,
) -> dict[str, Any]:
    """
    Send a single heartbeat to AgentOS.

    Args:
        base_url: Base URL of AgentOS API (e.g., "https://api.ag2.ai/api/v1")
        provider_name: Name of the agent provider
        endpoint_url: URL where the agent is accessible
        timeout: Request timeout in seconds
        console: Optional Rich console for styled output
        worker_type: Type of worker ("standalone" or "provisioned")
        worker_id: Unique worker ID (auto-generated if not provided)
        agent_card: Optional agent card to store in Redis
        worker_api_key: Optional API key for worker authentication

    Returns:
        Dictionary containing success status and worker_id
        {"success": True, "worker_id": "..."}
    """
    client = get_client_from_config()

    if base_url:
        client.base_url = base_url

    # Build payload
    payload: dict[str, Any] = {
        "provider_name": provider_name,
        "endpoint_url": endpoint_url,
    }

    if worker_type:
        payload["worker_type"] = worker_type

    if worker_id:
        payload["worker_id"] = worker_id

    if agent_card:
        payload["agent_card"] = agent_card

    # Build headers with optional API key
    headers = {"Content-Type": "application/json"}
    if worker_api_key:
        headers["Authorization"] = f"Bearer {worker_api_key}"

    try:
        print(f"Sending heartbeat to {base_url}/provisioner/heartbeat...")
        response = client.post(
            endpoint="/provisioner/heartbeat",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        response_data = response.json()

        # Extract worker_id from response
        returned_worker_id = response_data.get("worker_id", worker_id)

        if console:
            console.print(
                f"[green]✓[/green] Heartbeat sent (status: {response.status_code})"
            )
        else:
            print(f"Heartbeat sent, status code: {response.status_code}")

        return {"success": True, "worker_id": returned_worker_id}

    except httpx.HTTPError as e:
        if console:
            console.print(f"[yellow]⚠[/yellow] Failed to send heartbeat: {e}")
        else:
            print(f"Failed to send heartbeat: {e}")
        return {"success": False, "worker_id": worker_id}


async def heartbeat_loop(
    *,
    base_url: str,
    provider_name: str,
    endpoint_url: str,
    interval: int = 30,
    timeout: float = 10.0,
    console: Optional[Console] = None,
    worker_type: Optional[str] = None,
    worker_id: Optional[str] = None,
    agent_card: Optional[dict[str, Any]] = None,
    worker_api_key: Optional[str] = None,
) -> None:
    loop = asyncio.get_event_loop()
    current_worker_id = worker_id

    while True:
        # Run sync heartbeat in executor to avoid blocking
        try:
            result = await loop.run_in_executor(
                None,
                heartbeat_agentos,
                base_url,
                provider_name,
                endpoint_url,
                timeout,
                console,
                worker_type,
                current_worker_id,
                agent_card,
                worker_api_key,
            )

            # Update worker_id if returned from heartbeat
            if result.get("success") and result.get("worker_id"):
                current_worker_id = result["worker_id"]

        except BaseException as e:
            if console:
                console.print(f"[red]✗[/red] Heartbeat loop error: {e}")
            else:
                print(f"Heartbeat loop error: {e}")
        finally:
            # Wait for interval or until stop event is set
            await asyncio.sleep(interval)


def create_lifespan(
    *,
    base_url: Optional[str] = None,
    provider_name: Optional[str] = None,
    endpoint_url: Optional[str] = None,
    interval: int = 30,
    timeout: float = 10.0,
    console: Optional[Console] = None,
    worker_type: Optional[str] = None,
    worker_id: Optional[str] = None,
    agent_card: Optional[dict[str, Any]] = None,
    worker_api_key: Optional[str] = None,
) -> Any:
    config = get_config()
    final_base_url = base_url or config.agentos_base_url
    final_provider_name = provider_name or config.provider_name or "unknown-agent"
    final_endpoint_url = endpoint_url or config.server_url or "http://localhost:8000"
    final_worker_api_key = worker_api_key or config.worker_api_key

    @contextlib.asynccontextmanager
    async def lifespan(app: Any) -> Any:  # type: ignore[misc]
        # Startup actions
        print("Starting A2A Agent Server...")
        task = asyncio.create_task(
            heartbeat_loop(
                base_url=final_base_url,
                provider_name=final_provider_name,
                endpoint_url=final_endpoint_url,
                interval=interval,
                timeout=timeout,
                console=console,
                worker_type=worker_type,
                worker_id=worker_id,
                agent_card=agent_card,
                worker_api_key=final_worker_api_key,
            )
        )

        yield

        # Shutdown actions
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        print("Shutting down A2A Agent Server...")

    return lifespan


async def fetch_agent_card(
    server_url: str,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """
    Fetch the agent card from an A2A server.

    Args:
        server_url: Base URL of the A2A server
        timeout: Request timeout in seconds

    Returns:
        The agent card as a dictionary

    Raises:
        httpx.HTTPError: If the request fails
    """
    card_url = f"{server_url.rstrip('/')}/.well-known/agent-card.json"

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(card_url)
        response.raise_for_status()
        return response.json()


async def register_agent(
    *,
    a2a_server_url: str,
    agentos_base_url: str,
    provider_name: Optional[str] = None,
    console: Optional[Console] = None,
    worker_type: str = "standalone",
    worker_api_key: Optional[str] = None,
) -> tuple[dict[str, Any], str]:
    """
    Register an agent with AgentOS by fetching its card and sending initial heartbeat.

    This is a high-level helper that:
    1. Fetches the agent card from the A2A server
    2. Extracts provider name from the card if not provided
    3. Sends an initial heartbeat to register with AgentOS

    Args:
        a2a_server_url: Base URL of the A2A server
        agentos_base_url: Base URL of AgentOS API
        provider_name: Optional provider name (extracted from agent card if not provided)
        console: Optional Rich console for styled output
        worker_type: Type of worker ("standalone" or "provisioned"), defaults to "standalone"
        worker_api_key: Optional API key for worker authentication

    Returns:
        Tuple of (agent_card, worker_id)

    Raises:
        httpx.HTTPError: If fetching the agent card or registration fails
        RuntimeError: If heartbeat registration fails
    """
    # Fetch agent card
    agent_card = await fetch_agent_card(a2a_server_url)

    # Determine provider name
    final_name = provider_name or agent_card.get("name", "unknown-agent")

    if console:
        console.print(f"[cyan]Registering '{final_name}' with AgentOS...[/cyan]")

    # Send initial heartbeat to register
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        heartbeat_agentos,
        agentos_base_url,
        final_name,
        a2a_server_url,
        10.0,
        console,
        worker_type,
        None,  # worker_id will be auto-generated
        agent_card,
        worker_api_key,
    )

    if not result.get("success"):
        raise RuntimeError("Failed to register with AgentOS")

    worker_id = result.get("worker_id")
    if not worker_id:
        raise RuntimeError("No worker_id returned from registration")

    return agent_card, worker_id
