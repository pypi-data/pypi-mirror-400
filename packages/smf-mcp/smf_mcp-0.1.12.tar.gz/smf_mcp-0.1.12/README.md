# SMF - Enterprise MCP Framework

**SMF** is a production-ready Python framework built on top of [FastMCP](https://fastmcp.wiki/) that makes it significantly simpler to create, structure, and deploy MCP (Model Context Protocol) servers.

## Features

- 🏗️ **High-level abstractions**: `ServerFactory` and `AppBuilder` for minimal boilerplate
- 🔧 **Tool registration**: Simple decorator-based tool registration
- 🔌 **Plugin system**: Extensible architecture with stable interfaces
- 🚀 **CLI & Templates**: Project scaffolding and code generation
- 📦 **Simple & Focused**: Tools-only approach, no unnecessary complexity

## Architecture

```
┌─────────────────────────────┐
│   CLI & Templates           │
├─────────────────────────────┤
│  Extensions & Plugins       │
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
uv add smf-mcp
# or
pip install smf-mcp
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
    from smf.transport import run_server
    run_server(mcp)
```

### Advanced Server with AppBuilder

```python
from smf import AppBuilder

# Use AppBuilder for fluent registration
with AppBuilder() as builder:
    @builder.tool(tags=["math"])
    def add(a: float, b: float) -> float:
        """Add two numbers."""
        return a + b

    mcp = builder.build()

if __name__ == "__main__":
    from smf.transport import run_server
    run_server(mcp, transport="http", port=8000)
```

## CLI

```bash
# Initialize new project
smf init my-server

# Initialize project with Elasticsearch plugin
smf init my-server --elasticsearch --es-index "products"

# Run server
smf run server.py --transport http --port 8000

# Inspect server (Official Web Inspector)
smf inspector server.py
```

## Core Components

### ServerFactory

Creates configured FastMCP servers:

```python
from smf import ServerFactory

factory = ServerFactory()
mcp = factory.create(name="My Server")
```

### AppBuilder

Fluent interface for registering tools:

```python
from smf import AppBuilder

builder = AppBuilder()
builder.tool(my_function)
mcp = builder.build()
```

### Transport

Run servers with different transport mechanisms:

```python
from smf.transport import run_server

# Stdio (default)
run_server(mcp)

# HTTP
run_server(mcp, transport="http", host="0.0.0.0", port=8000)

# SSE
run_server(mcp, transport="sse", host="0.0.0.0", port=8000)
```

## Plugins

### Elasticsearch Plugin

Create Elasticsearch-powered MCP servers:

```bash
# Create server with CLI
smf init my-server --elasticsearch --es-index "products"

# Or use in code
from smf.plugins.elasticsearch import (
    ElasticsearchConfiguration,
    build_elasticsearch_connection,
    create_elasticsearch_tools,
)

es_config = ElasticsearchConfiguration.from_env()
es_client = build_elasticsearch_connection(es_config)
mcp = create_server("My Server")
tools = create_elasticsearch_tools(es_client, index="products")
for tool in tools:
    mcp.tool(tool)
```

Install: `pip install smf-mcp[elasticsearch]` or `uv add smf-mcp[elasticsearch]`

## Project Structure

When you initialize a new project with `smf init`, you get:

```
my-server/
├── src/
│   └── tools/
│       ├── __init__.py
│       └── tools.py          # Your tools
├── server.py                  # Main server file
└── README.md                  # Project documentation
```

## Requirements

- Python 3.11+
- FastMCP >= 2.11

## License

MIT

## Credits

Built on [FastMCP](https://fastmcp.wiki/) by Prefect.
