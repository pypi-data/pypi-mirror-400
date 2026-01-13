# AG2 CLI

A CLI tool for building, running, and deploying A2A-compatible agents.

## Installation

```bash
pip install ag2-cli
```

Or install from source:

```bash
git clone https://github.com/AG2Platform/ag2-cli.git
cd ag2-cli
pip install -e .
```

## Quick Start

### Create a new agent

```bash
ag2 init my-agent
cd my-agent
```

### Build and run with Docker

```bash
ag2 build
ag2 run
```

### Run natively (without Docker)

```bash
ag2 run --native
```

### Register with AgentOS

```bash
ag2 auth login
ag2 register https://my-agent.example.com
```

## Commands

### Authentication

```bash
ag2 auth login      # Login to AgentOS
ag2 auth logout     # Logout
ag2 auth whoami     # Show current user
```

### Agent Development

```bash
ag2 init [name]       # Create new agent project
ag2 create file.yaml  # Create agent from AgentFile
```

### Docker Lifecycle

```bash
ag2 build [path]    # Build agent Docker image
ag2 run [name]      # Run agent in Docker container
ag2 stop <name>     # Stop a running container
ag2 restart <name>  # Restart a container
ag2 logs <name>     # View container logs
ag2 ps              # List running containers
ag2 rm <name>       # Remove a container
ag2 rmi <name>      # Remove an image
ag2 images          # List built images
ag2 tag <src> <dst> # Tag an image
```

### Registry

```bash
ag2 register <url>  # Register running agent with AgentOS
ag2 agents          # List your registered agents
ag2 list            # List local agent images
```

### A2A Protocol

```bash
ag2 call <url> "message"  # Call any A2A agent
ag2 card show [path]      # Display agent card (from path or Docker image)
ag2 card validate [path]  # Validate A2A compliance
```

### Configuration

```bash
ag2 configure         # Interactive configuration wizard
ag2 config show       # Show current configuration
ag2 config set <k> <v> # Set configuration value
```

## AgentFile Format

The `agent.yaml` file defines your agent:

```yaml
name: "my-agent"
version: "1.0.0"
description: "My AI agent"

card:
  provider: "my-org"
  skills:
    - name: "default"
      description: "Default capability"
  auth:
    scheme: "bearer"

agent:
  model: "gpt-4o"
  system_prompt: |
    You are a helpful assistant.

build:
  python: "3.11"
  dependencies:
    - requests

deploy:
  replicas: 2
  memory: "1GB"
```

## A2A Protocol

This CLI generates A2A-compatible agents that implement:

- Agent Card at `/.well-known/a2a/agent-card.json`
- JSON-RPC 2.0 task endpoints
- SSE streaming support
- Standard authentication schemes

## Development

### Running tests

```bash
make test          # Run unit tests
make test-docker   # Run Docker lifecycle tests
make test-all      # Run all tests
```

### Documentation

```bash
make docs-install  # Install documentation dependencies
make docs          # Start local docs server
make docs-build    # Build documentation
```

## License

MIT
