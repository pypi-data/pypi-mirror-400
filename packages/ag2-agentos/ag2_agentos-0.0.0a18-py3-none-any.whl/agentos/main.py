"""AG2 CLI - Main entry point."""

from __future__ import annotations

import typer
from rich.console import Console


__version__ = "0.1.0"

from agentos.commands import agents, api_keys, deploy, login, register, secrets, workers

# Initialize Rich console for styled output
console = Console()


# Create main Typer app
app = typer.Typer(
    name="ag2",
    help="AG2 CLI - Agent development tool with A2A protocol support",
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)

# Add command groups
# Add authentication commands
app.command(name="login", help="Authenticate with AG2 using OAuth")(login.login)

# Add API keys management commands
app.add_typer(api_keys.app, name="api-keys", help="Manage API keys for authentication")

# Add top-level commands from agent module
app.add_typer(deploy.app, name="deploy", help="Deployment commands")
app.command(name="create")(deploy.deploy_create)

# Add secrets management commands
app.add_typer(secrets.app, name="secrets", help="Manage environment secrets")

# Add register command
app.command(name="register", help="Register agents with AgentOS")(register.register)

# Add agents command
app.add_typer(agents.app, name="agents", help="Manage agents")

# Add workers command
app.add_typer(workers.app, name="workers", help="Manage workers")

@app.command()
def version() -> None:
    """Show AG2 CLI version."""
    console.print(f"ag2 version {__version__}")


@app.callback()
def callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
) -> None:
    """
    AG2 CLI - Build, run, and deploy A2A-compatible agents.

    Inspired by Ollama's simplicity and Fly.io's deployment experience.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug


if __name__ == "__main__":
    app()
