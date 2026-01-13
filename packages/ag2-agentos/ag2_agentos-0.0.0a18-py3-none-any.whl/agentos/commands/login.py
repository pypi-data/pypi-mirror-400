"""Login command for AG2 CLI OAuth authentication."""

from __future__ import annotations

import secrets
import string
import webbrowser
from typing import Annotated

import typer
from rich.console import Console

from agentos.utils.config_manager import get_config_manager
from agentos.utils.oauth_server import OAuthCallbackServer
from agentos.config import get_config

console = Console()

app = typer.Typer(
    help="Authentication commands",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command(name="login")
def login(
    url: Annotated[str, typer.Option("--url", "-u", help="Authentication URL")] = None,
    port: Annotated[int, typer.Option("--port", "-p", help="Callback server port")] = 8617,
    timeout: Annotated[int, typer.Option("--timeout", "-t", help="Server timeout (seconds)")] = 300,
) -> None:
    """
    Authenticate with AG2 using OAuth.

    Opens a browser window for authentication and starts a local
    callback server to receive the access token.

    Example:
        ag2 login --url https://auth.ag2.ai
    """
    # 1. Generate 6-character security code
    code = generate_code()

    if url is None:
        config = get_config()
        url = config.agentos_base_url + "/cli-auth"

    # 2. Start OAuth server (with port fallback if port is occupied)
    try:
        server, actual_port = start_oauth_server(port, code, timeout)
    except Exception as e:
        console.print(f"[red]✗ Failed to start callback server: {e}[/red]")
        raise typer.Exit(1)

    # 3. Construct auth URL with query parameters
    auth_url = f"{url}?redirect_url=http://localhost:{actual_port}&code={code}"

    # 4. Open browser (with fallback to manual URL display)
    open_browser(auth_url)

    # 5. Wait for callback (blocking)
    console.print("[cyan]Waiting for authentication...[/cyan]")

    try:
        with console.status("[cyan]Listening for callback..."):
            server.start()
    except KeyboardInterrupt:
        console.print("\n[yellow]Authentication cancelled by user[/yellow]")
        server.shutdown()
        raise typer.Exit(0)
    # 6. Handle result
    if server.access_token and len(server.access_token) >= 10:
        try:
            config_mgr = get_config_manager()
            config_mgr.set_access_token(server.access_token)
            console.print("[green]✓ Successfully authenticated![/green]")
            console.print(f"[dim]Access token stored in ~/.ag2/config.ini[/dim]")
        except Exception as e:
            console.print(f"[red]✗ Failed to store access token: {e}[/red]")
            raise typer.Exit(1)
    elif server.error == "timeout":
        console.print("[red]✗ Authentication timed out after 5 minutes[/red]")
        console.print("[yellow]Please try again: ag2 login --url <url>[/yellow]")
        raise typer.Exit(1)
    else:
        console.print("[red]✗ Authentication failed[/red]")
        raise typer.Exit(1)


def generate_code(length: int = 6) -> str:
    """
    Generate cryptographically secure random code.

    Args:
        length: Length of code to generate (default: 6)

    Returns:
        Random alphanumeric code (uppercase letters and digits)
    """
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def start_oauth_server(port: int, code: str, timeout: int, max_retries: int = 5) -> tuple[OAuthCallbackServer, int]:
    """
    Start OAuth callback server with port fallback.

    Tries the specified port first, then tries sequential ports if occupied.

    Args:
        port: Initial port to try
        code: Expected security code
        timeout: Server timeout in seconds
        max_retries: Maximum number of ports to try

    Returns:
        Tuple of (OAuthCallbackServer instance, actual port used)

    Raises:
        OSError: If no available port found after max_retries
    """
    original_port = port

    for attempt in range(max_retries):
        try:
            server = OAuthCallbackServer(port, code, timeout)
            console.print(f"[dim]Callback server ready on port {port}[/dim]")
            return server, port

        except OSError as e:
            if "already in use" in str(e).lower():
                if attempt < max_retries - 1:
                    port += 1
                    console.print(f"[yellow]Port {port-1} in use, trying {port}...[/yellow]")
                else:
                    raise OSError(
                        f"Could not find available port (tried {original_port}-{port})"
                    ) from e
            else:
                raise

    # Should never reach here, but for type safety
    raise OSError(f"Failed to start server after {max_retries} attempts")


def open_browser(url: str) -> bool:
    """
    Open URL in browser with fallback to manual display.

    Args:
        url: URL to open

    Returns:
        True if browser opened successfully, False otherwise
    """
    console.print(f"[dim]Opening browser to: {url}[/dim]\n")

    try:
        success = webbrowser.open(url)
        if not success:
            # Browser opening failed, show manual instructions
            show_manual_url(url)
            return False
        return True

    except Exception as e:
        console.print(f"[yellow]⚠ Could not open browser: {e}[/yellow]")
        show_manual_url(url)
        return False


def show_manual_url(url: str) -> None:
    """
    Display URL for manual browser opening.

    Args:
        url: URL to display
    """
    console.print("[cyan]Please open this URL manually in your browser:[/cyan]")
    console.print(f"[bold]{url}[/bold]\n")
