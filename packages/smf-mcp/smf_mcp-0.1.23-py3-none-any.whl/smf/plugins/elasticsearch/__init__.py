"""
Elasticsearch Plugin for SMF.

Provides Elasticsearch integration for creating MCP servers with Elasticsearch tools.
"""

import json
from typing import Any, Callable, Dict, List, Optional, Union

_import_error = None
try:
    from elasticsearch import Elasticsearch
    # In elasticsearch 8.x+, ElasticsearchException was removed
    # Use Exception as base exception class for compatibility
    ElasticsearchException = Exception
    ELASTICSEARCH_AVAILABLE = True
except Exception as e:
    # Elasticsearch is an optional dependency - this is expected if not installed
    # Store the error for debugging (could be ImportError or other dependency issues)
    _import_error = e
    ELASTICSEARCH_AVAILABLE = False
    Elasticsearch = None
    ElasticsearchException = Exception


# ElasticsearchClient wrapper removed - not used by tools
# Tools created by create_elasticsearch_tools() use the native Elasticsearch client directly


def _to_plain(obj: Any) -> Any:
    """
    Convert Elasticsearch response objects to plain Python types (dict, list, etc.)
    that are JSON-serializable.
    
    Handles ObjectApiResponse from elasticsearch 8.x+ which wraps responses.
    
    Args:
        obj: Response object from Elasticsearch client
        
    Returns:
        Plain Python object (dict, list, etc.) that can be JSON-serialized
    """
    try:
        from elastic_transport import ObjectApiResponse
    except ImportError:
        ObjectApiResponse = None
    
    if ObjectApiResponse is not None and isinstance(obj, ObjectApiResponse):
        # For ES 8.x+ clients, convert ObjectApiResponse to dict
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        elif hasattr(obj, "body"):
            return obj.body
        # Fallback: try to access as dict-like
        return dict(obj) if hasattr(obj, "__iter__") else obj
    
    # Already a plain type (dict, list, str, int, etc.)
    return obj


def create_elasticsearch_tools(
    es_client: "Elasticsearch",
    index: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> List[Callable]:
    """
    Create read-only Elasticsearch tools for SMF.

    Provides tools for searching, reading documents, listing indices, checking cluster health,
    executing Query DSL queries, and running ES|QL queries.
    All tools are read-only and do not modify data.

    Args:
        es_client: Native Elasticsearch client instance (from elasticsearch import Elasticsearch)
        index: Default index name (optional)
        tags: Tags to apply to tools

    Returns:
        List of read-only tool functions ready to be registered with @mcp.tool

    Example:
        >>> from elasticsearch import Elasticsearch
        >>> es_client = Elasticsearch("http://localhost:9200")
        >>> tools = create_elasticsearch_tools(es_client, index="my_index")
        >>> for tool in tools:
        ...     mcp.tool(tool)
    """
    tags = tags or ["elasticsearch"]
    
    # Use the native Elasticsearch client directly
    client = es_client

    def search_tool(
        query: str,
        index_name: Optional[str] = None,
        size: int = 10,
    ) -> Dict[str, Any]:
        """
        Search documents in Elasticsearch.

        Args:
            query: Search query (will be converted to match query)
            index_name: Index name (uses default if not provided)
            size: Number of results to return

        Returns:
            Search results
        """
        target_index = index_name or index
        if not target_index:
            raise ValueError("Index name is required")

        # Use match_all with query_string for better compatibility
        # Use native Elasticsearch API
        # For Elasticsearch 8.x+, use direct parameters; for older versions, use body=
        try:
            # Try modern API first (Elasticsearch 8.x+)
            response = client.search(
                index=target_index,
                query={"query_string": {"query": query}},
                size=size
            )
        except TypeError:
            # Fallback to body parameter for older versions
            es_query = {"query": {"query_string": {"query": query}}}
            response = client.search(index=target_index, body=es_query, size=size)
        return _to_plain(response)

    def get_document_tool(
        document_id: str,
        index_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get a document by ID.

        Args:
            document_id: Document ID
            index_name: Index name (uses default if not provided)

        Returns:
            Document data
        """
        target_index = index_name or index
        if not target_index:
            raise ValueError("Index name is required")

        # Use native Elasticsearch API
        response = client.get(index=target_index, id=document_id)
        return _to_plain(response)

    def list_indices_tool(pattern: Optional[str] = None) -> List[str]:
        """
        List Elasticsearch indices.

        Args:
            pattern: Optional index pattern (supports wildcards)

        Returns:
            List of index names
        """
        # Use native Elasticsearch API
        if pattern:
            response = _to_plain(client.indices.get_alias(index=pattern))
        else:
            response = _to_plain(client.indices.get_alias())
        # Extract keys from the response dict
        if isinstance(response, dict):
            return list(response.keys())
        # Fallback: if response is already a list or something else
        return list(response) if isinstance(response, (list, tuple)) else []

    def cluster_health_tool() -> Dict[str, Any]:
        """
        Get Elasticsearch cluster health.

        Returns:
            Cluster health information
        """
        # Use native Elasticsearch API
        response = client.cluster.health()
        return _to_plain(response)

    def query_dsl_search_tool(
        query_dsl: str,
        index_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute an Elasticsearch Query DSL search query.
        
        This tool allows you to write complex Elasticsearch queries using the full Query DSL.
        The query_dsl parameter should be a JSON string representing the complete query DSL.
        
        Args:
            query_dsl: Complete Elasticsearch Query DSL as a JSON string.
                      Example: '{"query": {"match": {"title": "python"}}, "size": 10}'
            index_name: Index name (uses default if not provided)
        
        Returns:
            Search results from Elasticsearch
            
        Example query_dsl:
            {
                "query": {
                    "bool": {
                        "must": [{"match": {"title": "python"}}],
                        "filter": [{"term": {"status": "published"}}]
                    }
                },
                "size": 20,
                "sort": [{"date": {"order": "desc"}}]
            }
        """
        target_index = index_name or index
        if not target_index:
            raise ValueError("Index name is required")
        
        # Parse the JSON query DSL
        try:
            query_dict = json.loads(query_dsl)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in query_dsl: {e}. Please provide valid JSON.")
        
        # Execute the query using body parameter (compatible with all ES versions)
        # For ES 8.x+, we could use direct parameters, but body works for all versions
        try:
            # Try modern API first (ES 8.x+) with body parameter
            response = client.search(index=target_index, body=query_dict)
        except TypeError:
            # Fallback: some ES 8.x+ clients might not accept body, try direct params
            try:
                if "query" in query_dict:
                    query = query_dict.get("query")
                    # Extract common parameters
                    search_params = {k: v for k, v in query_dict.items() 
                                   if k in ["size", "from", "sort", "aggs", "aggregations", "_source", "highlight", "track_total_hits"]}
                    response = client.search(
                        index=target_index,
                        query=query,
                        **search_params
                    )
                else:
                    # No query field, use match_all
                    response = client.search(
                        index=target_index,
                        query={"match_all": {}},
                        **{k: v for k, v in query_dict.items() if k in ["size", "from", "sort", "aggs"]}
                    )
            except (TypeError, AttributeError):
                # Final fallback: use body with older API style
                response = client.search(index=target_index, body=query_dict)
        
        return _to_plain(response)

    def esql_query_tool(
        esql_query: str,
    ) -> Dict[str, Any]:
        """
        Execute an Elasticsearch ES|QL (Elasticsearch Query Language) query.
        
        ES|QL is a powerful query language for Elasticsearch that allows you to write
        SQL-like queries. This tool accepts a raw ES|QL query string.
        
        Args:
            esql_query: ES|QL query string.
                       Example: 'FROM my-index | WHERE user.id == "kimchy" | STATS count() BY status'
        
        Returns:
            Query results from Elasticsearch
            
        Example esql_query:
            FROM my-index-*
            | WHERE status == "active"
            | STATS count() BY category
            | SORT count() DESC
            | LIMIT 10
            
        Note: ES|QL is available in Elasticsearch 8.11+ and 9.0+.
        """
        # Check if ES|QL API is available (ES 8.11+ or 9.0+)
        if not hasattr(client, "esql"):
            raise ValueError(
                "ES|QL API is not available. ES|QL requires Elasticsearch 8.11+ or 9.0+. "
                "Your client version may not support ES|QL, or your cluster version is too old."
            )
        
        try:
            # Execute ES|QL query
            response = client.esql.query(query=esql_query)
        except AttributeError:
            raise ValueError(
                "ES|QL API is not available on this Elasticsearch client. "
                "Please ensure you're using elasticsearch>=8.11.0 or elasticsearch>=9.0.0"
            )
        except Exception as e:
            raise ValueError(f"ES|QL query execution failed: {e}")
        
        return _to_plain(response)

    # Add tags to docstrings
    for tool in [
        search_tool,
        get_document_tool,
        list_indices_tool,
        cluster_health_tool,
        query_dsl_search_tool,
        esql_query_tool,
    ]:
        if hasattr(tool, "__doc__"):
            tool.__doc__ = f"{tool.__doc__}\n\nTags: {', '.join(tags)}"

    return [
        search_tool,
        get_document_tool,
        list_indices_tool,
        cluster_health_tool,
        query_dsl_search_tool,
        esql_query_tool,
    ]

# Export configuration and connection utilities
from smf.plugins.elasticsearch.elasticsearch_configuration import (
    ElasticsearchConfiguration,
)
from smf.plugins.elasticsearch.connection import (
    build_elasticsearch_connection,
    build_elasticsearch_connection_async,
)
from smf.plugins.elasticsearch.version_check import (
    ElasticsearchVersionMismatchError,
    get_client_version,
    get_cluster_version,
    check_version_compatibility,
)

__all__ = [
    "ElasticsearchConfiguration",
    "build_elasticsearch_connection",
    "build_elasticsearch_connection_async",
    "create_elasticsearch_tools",
    "ElasticsearchVersionMismatchError",
    "get_client_version",
    "get_cluster_version",
    "check_version_compatibility",
]
