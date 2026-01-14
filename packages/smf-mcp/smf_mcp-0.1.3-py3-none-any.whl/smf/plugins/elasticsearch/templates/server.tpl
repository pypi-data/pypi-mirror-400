"""
SMF Elasticsearch Server - Main entry point.

This server provides Elasticsearch tools for the "{default_index}" index.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from smf import create_server

# Try to import Elasticsearch plugin
try:
    from smf.plugins.elasticsearch import (
        ElasticsearchClient,
        create_elasticsearch_tools,
    )
except ImportError:
    print("Error: elasticsearch plugin not installed.")
    print("Install with: pip install smf-mcp[elasticsearch] or uv add smf-mcp[elasticsearch]")
    sys.exit(1)

# Create Elasticsearch client
# Configuration via environment variables:
# - ELASTICSEARCH_HOSTS: Elasticsearch host(s) (default: {es_hosts})
# - ELASTICSEARCH_API_KEY: Optional API key
# - ELASTICSEARCH_USERNAME: Optional username for basic auth
# - ELASTICSEARCH_PASSWORD: Optional password for basic auth

es_hosts = os.getenv("ELASTICSEARCH_HOSTS", "{es_hosts}")
es_config = {{"hosts": es_hosts}}

# Add authentication if provided
if os.getenv("ELASTICSEARCH_API_KEY"):
    es_config["api_key"] = os.getenv("ELASTICSEARCH_API_KEY")
elif os.getenv("ELASTICSEARCH_USERNAME") and os.getenv("ELASTICSEARCH_PASSWORD"):
    es_config["basic_auth"] = (
        os.getenv("ELASTICSEARCH_USERNAME"),
        os.getenv("ELASTICSEARCH_PASSWORD"),
    )

try:
    es_client = ElasticsearchClient(**es_config)
    print(f"✓ Connected to Elasticsearch at {{es_hosts}}")
except Exception as e:
    print(f"Error connecting to Elasticsearch: {{e}}")
    print("Make sure Elasticsearch is running and accessible.")
    sys.exit(1)

# Create SMF server
mcp = create_server("{server_name}")

# Create and register Elasticsearch tools
print(f"✓ Registering Elasticsearch tools for index: {default_index}")
es_tools = create_elasticsearch_tools(
    es_client=es_client,
    index="{default_index}",
    tags=["elasticsearch", "search"],
)

for tool in es_tools:
    mcp.tool(tool)

# You can add custom Elasticsearch tools here
# Example:
# @mcp.tool(tags=["elasticsearch", "custom"])
# def custom_search(query: str, filters: dict = None) -> dict:
#     \"\"\"Custom search with filters.\"\"\"
#     es_query = {{"query": {{"match": {{"_all": query}}}}}}
#     if filters:
#         es_query["query"]["bool"] = {{"filter": filters}}
#     return es_client.search(index="{default_index}", query=es_query)

print(f"✓ Server '{server_name}' ready with {{len(es_tools)}} Elasticsearch tools")
print(f"✓ Default index: {default_index}")

if __name__ == "__main__":
    mcp.run()
