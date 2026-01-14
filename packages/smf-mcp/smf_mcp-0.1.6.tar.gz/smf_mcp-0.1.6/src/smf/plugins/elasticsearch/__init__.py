"""
Elasticsearch Plugin for SMF.

Provides Elasticsearch integration for creating MCP servers with Elasticsearch tools.
"""

from typing import Any, Dict, List, Optional, Union

_import_error = None
try:
    from elasticsearch import Elasticsearch
    from elasticsearch.exceptions import ElasticsearchException
    ELASTICSEARCH_AVAILABLE = True
except Exception as e:
    # Elasticsearch is an optional dependency - this is expected if not installed
    # Store the error for debugging (could be ImportError or other dependency issues)
    _import_error = e
    ELASTICSEARCH_AVAILABLE = False
    Elasticsearch = None
    ElasticsearchException = Exception


class ElasticsearchClient:
    """
    Elasticsearch client wrapper for SMF.
    
    Provides a convenient interface for Elasticsearch operations.
    """

    def __init__(
        self,
        hosts: Union[str, List[str]] = "http://localhost:9200",
        **kwargs: Any,
    ):
        """
        Initialize Elasticsearch client.

        Args:
            hosts: Elasticsearch host(s). Can be a string or list of strings.
            **kwargs: Additional Elasticsearch client parameters.
                    Common options:
                    - api_key: API key for authentication
                    - basic_auth: Tuple of (username, password)
                    - verify_certs: Whether to verify SSL certificates
                    - ssl_show_warn: Show SSL warnings
                    - timeout: Request timeout in seconds
                    - max_retries: Maximum number of retries
                    - retry_on_timeout: Whether to retry on timeout

        Raises:
            ImportError: If elasticsearch package is not installed
        """
        # Try to import elasticsearch again in case it wasn't available at module load time
        global ELASTICSEARCH_AVAILABLE, Elasticsearch, ElasticsearchException, _import_error
        if not ELASTICSEARCH_AVAILABLE:
            try:
                import sys
                import importlib
                # Force reload if already imported (might have failed before)
                if 'elasticsearch' in sys.modules:
                    importlib.reload(sys.modules['elasticsearch'])
                from elasticsearch import Elasticsearch as _Elasticsearch
                from elasticsearch.exceptions import ElasticsearchException as _ElasticsearchException
                Elasticsearch = _Elasticsearch
                ElasticsearchException = _ElasticsearchException
                ELASTICSEARCH_AVAILABLE = True
            except Exception as e:
                error_msg = (
                    f"elasticsearch package is required but import failed: {type(e).__name__}: {e}. "
                    f"Install with: pip install smf-mcp[elasticsearch] or uv add smf-mcp[elasticsearch]"
                )
                # Include original error if available
                if _import_error is not None:
                    error_msg += f"\nOriginal import error at module load: {type(_import_error).__name__}: {_import_error}"
                raise ImportError(error_msg) from e

        # Convert single host string to list if needed
        if isinstance(hosts, str):
            hosts = [hosts]

        self.client = Elasticsearch(hosts=hosts, **kwargs)
        self._test_connection()

    def _test_connection(self) -> None:
        """Test Elasticsearch connection."""
        try:
            if not self.client.ping():
                raise ConnectionError("Cannot connect to Elasticsearch cluster")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Elasticsearch: {e}")

    def search(
        self,
        index: str,
        query: Dict[str, Any],
        size: int = 10,
        from_: int = 0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute a search query.

        Args:
            index: Index name or pattern (supports wildcards)
            query: Elasticsearch query DSL
            size: Number of results to return
            from_: Starting offset
            **kwargs: Additional search parameters

        Returns:
            Search results dictionary

        Raises:
            ElasticsearchException: If search fails
        """
        try:
            response = self.client.search(
                index=index,
                body=query,
                size=size,
                from_=from_,
                **kwargs,
            )
            return response
        except ElasticsearchException as e:
            raise ValueError(f"Elasticsearch search failed: {e}")

    def get_document(
        self,
        index: str,
        document_id: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Get a document by ID.

        Args:
            index: Index name
            document_id: Document ID
            **kwargs: Additional get parameters

        Returns:
            Document dictionary

        Raises:
            ElasticsearchException: If document retrieval fails
        """
        try:
            response = self.client.get(index=index, id=document_id, **kwargs)
            return response
        except ElasticsearchException as e:
            raise ValueError(f"Failed to get document: {e}")

    def index_document(
        self,
        index: str,
        document: Dict[str, Any],
        document_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Index a document.

        Args:
            index: Index name
            document: Document to index
            document_id: Optional document ID (auto-generated if None)
            **kwargs: Additional index parameters

        Returns:
            Index response dictionary

        Raises:
            ElasticsearchException: If indexing fails
        """
        try:
            if document_id:
                response = self.client.index(
                    index=index, id=document_id, body=document, **kwargs
                )
            else:
                response = self.client.index(index=index, body=document, **kwargs)
            return response
        except ElasticsearchException as e:
            raise ValueError(f"Failed to index document: {e}")

    def update_document(
        self,
        index: str,
        document_id: str,
        doc: Dict[str, Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Update a document.

        Args:
            index: Index name
            document_id: Document ID
            doc: Document fields to update
            **kwargs: Additional update parameters

        Returns:
            Update response dictionary

        Raises:
            ElasticsearchException: If update fails
        """
        try:
            response = self.client.update(
                index=index, id=document_id, body={"doc": doc}, **kwargs
            )
            return response
        except ElasticsearchException as e:
            raise ValueError(f"Failed to update document: {e}")

    def delete_document(
        self,
        index: str,
        document_id: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Delete a document.

        Args:
            index: Index name
            document_id: Document ID
            **kwargs: Additional delete parameters

        Returns:
            Delete response dictionary

        Raises:
            ElasticsearchException: If deletion fails
        """
        try:
            response = self.client.delete(index=index, id=document_id, **kwargs)
            return response
        except ElasticsearchException as e:
            raise ValueError(f"Failed to delete document: {e}")

    def get_indices(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get list of indices.

        Args:
            pattern: Optional index pattern (supports wildcards)

        Returns:
            List of index names

        Raises:
            ElasticsearchException: If request fails
        """
        try:
            if pattern:
                indices = list(self.client.indices.get_alias(index=pattern).keys())
            else:
                indices = list(self.client.indices.get_alias().keys())
            return indices
        except ElasticsearchException as e:
            raise ValueError(f"Failed to get indices: {e}")

    def get_index_info(self, index: str) -> Dict[str, Any]:
        """
        Get index information.

        Args:
            index: Index name

        Returns:
            Index information dictionary

        Raises:
            ElasticsearchException: If request fails
        """
        try:
            response = self.client.indices.get(index=index)
            return response[index]
        except ElasticsearchException as e:
            raise ValueError(f"Failed to get index info: {e}")

    def cluster_health(self) -> Dict[str, Any]:
        """
        Get cluster health.

        Returns:
            Cluster health dictionary

        Raises:
            ElasticsearchException: If request fails
        """
        try:
            return self.client.cluster.health()
        except ElasticsearchException as e:
            raise ValueError(f"Failed to get cluster health: {e}")

    def close(self) -> None:
        """Close Elasticsearch client connection."""
        if self.client:
            self.client.close()


def create_elasticsearch_tools(
    es_client: ElasticsearchClient,
    index: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> List[callable]:
    """
    Create common Elasticsearch tools for SMF.

    Args:
        es_client: ElasticsearchClient instance
        index: Default index name (optional)
        tags: Tags to apply to tools

    Returns:
        List of tool functions ready to be registered with @mcp.tool

    Example:
        >>> es_client = ElasticsearchClient(hosts="http://localhost:9200")
        >>> tools = create_elasticsearch_tools(es_client, index="my_index")
        >>> for tool in tools:
        ...     mcp.tool(tool)
    """
    tags = tags or ["elasticsearch"]

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

        es_query = {"query": {"match": {"_all": query}}}
        return es_client.search(index=target_index, query=es_query, size=size)

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

        return es_client.get_document(index=target_index, document_id=document_id)

    def index_document_tool(
        document: Dict[str, Any],
        index_name: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Index a document.

        Args:
            document: Document to index
            index_name: Index name (uses default if not provided)
            document_id: Optional document ID

        Returns:
            Index response
        """
        target_index = index_name or index
        if not target_index:
            raise ValueError("Index name is required")

        return es_client.index_document(
            index=target_index, document=document, document_id=document_id
        )

    def list_indices_tool(pattern: Optional[str] = None) -> List[str]:
        """
        List Elasticsearch indices.

        Args:
            pattern: Optional index pattern (supports wildcards)

        Returns:
            List of index names
        """
        return es_client.get_indices(pattern=pattern)

    def cluster_health_tool() -> Dict[str, Any]:
        """
        Get Elasticsearch cluster health.

        Returns:
            Cluster health information
        """
        return es_client.cluster_health()

    # Add tags to docstrings
    for tool in [search_tool, get_document_tool, index_document_tool, list_indices_tool, cluster_health_tool]:
        if hasattr(tool, "__doc__"):
            tool.__doc__ = f"{tool.__doc__}\n\nTags: {', '.join(tags)}"

    return [
        search_tool,
        get_document_tool,
        index_document_tool,
        list_indices_tool,
        cluster_health_tool,
    ]


def create_elasticsearch_client_from_config(
    config: Dict[str, Any],
) -> ElasticsearchClient:
    """
    Create ElasticsearchClient from configuration dictionary.

    Args:
        config: Configuration dictionary with keys:
                - hosts: Elasticsearch host(s)
                - api_key: Optional API key
                - basic_auth: Optional tuple (username, password)
                - verify_certs: Optional SSL verification
                - timeout: Optional timeout
                - max_retries: Optional max retries

    Returns:
        ElasticsearchClient instance

    Example:
        >>> config = {
        ...     "hosts": "http://localhost:9200",
        ...     "api_key": "your-api-key",
        ...     "timeout": 30
        ... }
        >>> es_client = create_elasticsearch_client_from_config(config)
    """
    hosts = config.get("hosts", "http://localhost:9200")
    kwargs = {}

    if "api_key" in config:
        kwargs["api_key"] = config["api_key"]
    if "basic_auth" in config:
        kwargs["basic_auth"] = config["basic_auth"]
    if "verify_certs" in config:
        kwargs["verify_certs"] = config["verify_certs"]
    if "timeout" in config:
        kwargs["timeout"] = config["timeout"]
    if "max_retries" in config:
        kwargs["max_retries"] = config["max_retries"]

    return ElasticsearchClient(hosts=hosts, **kwargs)


# CLI commands - no longer needed, use smf init --elasticsearch instead
def add_parser(subparsers):
    """No-op: activate-plugin command removed. Use 'smf init --elasticsearch' instead."""
    pass


__all__ = [
    "ElasticsearchClient",
    "create_elasticsearch_client_from_config",
    "create_elasticsearch_tools",
    "add_parser",
]
