"""
SMF Elasticsearch Server - Main entry point.

This server provides Elasticsearch tools for the "{default_index}" index,
along with example tools, resources, and prompts.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from smf import create_server
from smf.settings import get_settings

get_settings(base_dir=Path(__file__).parent)

# Create SMF server
mcp = create_server("{server_name}")

# Import example components
from tools.tools import greet as greet_tool, calculate as calculate_tool
from resources.resources import get_server_info
from prompts.prompts import system_prompt

# Register example tools
@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return greet_tool(name)

@mcp.tool
def calculate(operation: str, a: float, b: float) -> float:
    """Perform a calculation."""
    return calculate_tool(operation, a, b)

# Register example resources
@mcp.resource("server://info")
def server_info() -> str:
    """Get server information."""
    return get_server_info()

# Register example prompts
@mcp.prompt
def system() -> str:
    """System prompt template."""
    return system_prompt()

# Try to import Elasticsearch plugin
try:
    from smf.plugins.elasticsearch import (
        ElasticsearchConfiguration,
        build_elasticsearch_connection,
        create_elasticsearch_tools,
    )
except ImportError:
    print("Warning: elasticsearch plugin not installed.")
    print("Install with: pip install smf-mcp[elasticsearch] or uv add smf-mcp[elasticsearch]")
    print("Server will run without Elasticsearch tools.")
else:
    # Create Elasticsearch configuration from environment variables
    # The .env file is automatically loaded by python-dotenv
    # Configuration via environment variables:
    # - ELASTICSEARCH_HOSTS: Elasticsearch host(s) (default: {es_hosts})
    # - ELASTICSEARCH_API_KEY: Optional API key
    # - ELASTICSEARCH_USERNAME: Optional username for basic auth
    # - ELASTICSEARCH_PASSWORD: Optional password for basic auth
    # - ELASTICSEARCH_VERIFY_CERTS: Verify SSL certificates (default: true)
    # - ELASTICSEARCH_TIMEOUT: Request timeout in seconds
    # - ELASTICSEARCH_MAX_RETRIES: Maximum retries (default: 3)

    try:
        # Load configuration from environment variables (automatically loads .env)
        es_config = ElasticsearchConfiguration.from_env()
        
        # Build Elasticsearch client connection
        es_client = build_elasticsearch_connection(es_config)
        
        print(f"✓ Connected to Elasticsearch at {{es_config.hosts}}")
        
        # Create and register Elasticsearch tools
        print(f"✓ Registering Elasticsearch tools for index: {default_index}")
        es_tools = create_elasticsearch_tools(
            es_client=es_client,
            index="{default_index}",
            tags=["elasticsearch", "search"],
        )

        for tool in es_tools:
            mcp.tool(tool)

        print(f"✓ Registered {{len(es_tools)}} Elasticsearch tools")
        print(f"✓ Default index: {default_index}")
    except ImportError as e:
        print(f"Warning: Elasticsearch package not available: {{e}}")
        print("Install with: pip install smf-mcp[elasticsearch] or uv add smf-mcp[elasticsearch]")
        print("Server will run without Elasticsearch tools.")
    except Exception as e:
        print(f"Warning: Error connecting to Elasticsearch: {{e}}")
        print("Server will run without Elasticsearch tools.")
        print("Make sure Elasticsearch is running and accessible.")
        print("Check your .env file or environment variables for configuration.")

# You can add custom Elasticsearch tools here
# Example:
# @mcp.tool(tags=["elasticsearch", "custom"])
# def custom_search(query: str, filters: dict = None) -> dict:
#     \"\"\"Custom search with filters.\"\"\"
#     es_query = {{"query": {{"match": {{"_all": query}}}}}}
#     if filters:
#         es_query["query"]["bool"] = {{"filter": filters}}
#     return es_client.search(index="{default_index}", query=es_query)

if __name__ == "__main__":
    import argparse
    from smf.transport import run_server

    parser = argparse.ArgumentParser(description="Run SMF server")
    parser.add_argument("--transport", help="Transport type")
    parser.add_argument("--host", help="HTTP host")
    parser.add_argument("--port", type=int, help="HTTP port")
    args = parser.parse_args()

    run_kwargs = {{}}
    if args.transport:
        run_kwargs["transport"] = args.transport
    if args.host:
        run_kwargs["host"] = args.host
    if args.port is not None:
        run_kwargs["port"] = args.port

    run_server(mcp, **run_kwargs)
