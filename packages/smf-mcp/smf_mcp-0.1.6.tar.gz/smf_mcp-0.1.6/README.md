# SMF - Enterprise MCP Framework

**SMF** is a production-ready Python framework built on top of [FastMCP](https://fastmcp.wiki/) that makes it significantly simpler and more professional to create, structure, and deploy MCP (Model Context Protocol) servers in enterprise production environments.

## Features

- 🏗️ **High-level abstractions**: `ServerFactory` and `AppBuilder` for minimal boilerplate
- 🔧 **Modular registration**: Filesystem conventions, explicit registries, and plugin discovery
- ⚙️ **Production runtime**: Configuration system, structured logging, health endpoints, lifecycle management
- 🔐 **Enterprise auth**: Pluggable authentication (JWT, OAuth, OIDC) and authorization policies
- 🔄 **Middleware pipeline**: Chain of Responsibility pattern for logging, metrics, rate limiting, error handling
- 🔌 **Plugin system**: Extensible architecture with stable interfaces
- 📊 **Observability**: Prometheus metrics, OpenTelemetry tracing, structured logging
- 🚀 **CLI & Templates**: Project scaffolding and code generation

## Architecture

```
┌─────────────────────────────┐
│   CLI & Templates           │
├─────────────────────────────┤
│ Integrations (AuthZ, AI SDK) │
├─────────────────────────────┤
│  Extensions & Middleware    │
├─────────────────────────────┤
│    Core SMF Layer          │
├─────────────────────────────┤
│    FastMCP (Upstream)        │
└─────────────────────────────┘
```

SMF wraps FastMCP without modifying it, ensuring compatibility with FastMCP updates while adding enterprise features.

## Quick Start

### Installation

```bash
uv add smf fastmcp
```

### Simple Server

```python
from smf import create_server

# Create server
mcp = create_server("My Server")

# Register a tool
@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

### Advanced Server with AppBuilder

```python
from smf import AppBuilder, Settings

# Custom settings
settings = Settings(
    server_name="My Server",
    structured_logging=True,
    metrics_enabled=True,
    rate_limit_enabled=True,
)

# Use AppBuilder
with AppBuilder(settings=settings) as builder:
    @builder.tool(tags=["math"])
    def add(a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
    
    mcp = builder.build()

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
```

## Configuration

SMF uses Pydantic-based settings that can be loaded from:

- Environment variables (prefix: `SMF_`)
- `.env` files
- YAML/JSON configuration files

```yaml
# smf.yaml
server_name: "My Server"
server_version: "1.0.0"
transport: "http"
host: "0.0.0.0"
port: 8000
structured_logging: true
metrics_enabled: true
rate_limit_enabled: true
rate_limit_per_minute: 100
auth_provider: "jwt"
auth_config:
  secret: "${JWT_SECRET}"
```

## CLI

```bash
# Initialize new project
smf init my-server

# Initialize project with Elasticsearch plugin
smf init my-server --elasticsearch --es-index "products"

# Add a tool
smf add-tool my-tool --description "Tool description"

# Validate configuration (syntax and values)
smf validate --config smf.yaml

# Validate with comprehensive tests
smf validate --config smf.yaml --tests

# Run server
smf run server.py --transport http --port 8000

# Inspect server (Official Web Inspector)
smf inspector server.py
```

## Core Components

### ServerFactory

Creates configured FastMCP servers with defaults applied:

```python
from smf import ServerFactory, Settings

factory = ServerFactory(settings=Settings())
mcp = factory.create(name="My Server")
```

### AppBuilder

Fluent interface for registering components:

```python
from smf import AppBuilder

builder = AppBuilder()
builder.tool(my_function)
builder.resource(my_resource)
mcp = builder.build()
```

### Settings

Centralized configuration management:

```python
from smf import Settings

settings = Settings(
    server_name="My Server",
    structured_logging=True,
    metrics_enabled=True,
)
```

## Middleware

SMF provides built-in middleware:

- **StructuredLoggingMiddleware**: JSON-structured logging
- **TracingMiddleware**: OpenTelemetry distributed tracing
- **RateLimitingMiddleware**: Token bucket rate limiting
- **ErrorHandlingMiddleware**: Normalized error responses
- **MetricsMiddleware**: Prometheus metrics collection

## Authentication

Pluggable authentication providers:

```python
from smf import Settings, AuthProvider

settings = Settings(
    auth_provider=AuthProvider.JWT,
    auth_config={
        "secret": "your-secret-key",
        "algorithm": "HS256",
    }
)
```

Supported providers:
- JWT
- OAuth
- OIDC (via TokenVerifier)
- Custom providers

## Plugins

### Elasticsearch Plugin

Create Elasticsearch-powered MCP servers:

```bash
# Create server with CLI
smf init my-server --elasticsearch --es-index "products"

# Or use in code
from smf.plugins.elasticsearch import ElasticsearchClient, create_elasticsearch_tools

es_client = ElasticsearchClient(hosts="http://localhost:9200")
mcp = create_server("My Server")
tools = create_elasticsearch_tools(es_client, index="products")
for tool in tools:
    mcp.tool(tool)
```

Install: `pip install smf-mcp[elasticsearch]`

See [Elasticsearch Plugin Documentation](./src/docs/plugins-elasticsearch.md) for details.

## Examples

See `src/examples/` for:
- `simple_server/`: Basic server setup
- `advanced_server/`: Advanced patterns with custom settings

## Documentation

- [FastMCP Research](./src/docs/fastmcp-research.md): FastMCP API mapping
- [Architecture](./help.md): Detailed architecture documentation

## Requirements

- Python 3.11+
- FastMCP >= 2.11

## Development

```bash
# Install dependencies
uv sync --dev

# Run tests
pytest

# Format code
black src/

# Type check
mypy src/
```

## License

MIT

## Credits

Built on [FastMCP](https://fastmcp.wiki/) by Prefect.

