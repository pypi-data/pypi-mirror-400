"""AG2 CLI - Main entry point."""

__version__ = "0.1.0"

# Export config system
from agentos.config import AG2Config, Platform, get_config, reload_config

# Export HTTP client
from agentos.client import AG2Client, get_client

# Export heartbeat utilities
from agentos.utils.heartbeat import (
    create_lifespan,
    fetch_agent_card,
    heartbeat_agentos,
    heartbeat_loop,
    register_agent,
)

__all__ = [
    "__version__",
    # Config
    "AG2Config",
    "Platform",
    "get_config",
    "reload_config",
    # HTTP Client
    "AG2Client",
    "get_client",
    # Heartbeat utilities
    "heartbeat_agentos",
    "heartbeat_loop",
    "create_lifespan",
    "fetch_agent_card",
    "register_agent",
]
