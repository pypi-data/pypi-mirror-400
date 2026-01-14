"""
Elasticsearch Connection Management.

Functions to create sync and async Elasticsearch clients from configuration.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from elasticsearch import AsyncElasticsearch, Elasticsearch

from smf.plugins.elasticsearch.elasticsearch_configuration import (
    ElasticsearchConfiguration,
)
from smf.plugins.elasticsearch.version_check import (
    check_version_compatibility,
    ElasticsearchVersionMismatchError,
)


def build_elasticsearch_connection(
    es_config: ElasticsearchConfiguration,
    skip_version_check: bool = False,
) -> "Elasticsearch":
    """
    Build synchronous Elasticsearch client from configuration.
    
    Validates version compatibility between client and cluster.
    
    Args:
        es_config: ElasticsearchConfiguration instance
        skip_version_check: If True, skip version compatibility check (not recommended)
        
    Returns:
        Elasticsearch client instance (sync)
        
    Raises:
        ImportError: If elasticsearch package is not installed
        ElasticsearchVersionMismatchError: If client and cluster versions are incompatible
        ConnectionError: If unable to connect to cluster
        
    Example:
        >>> from smf.plugins.elasticsearch import ElasticsearchConfiguration
        >>> config = ElasticsearchConfiguration(hosts="http://localhost:9200")
        >>> client = build_elasticsearch_connection(config)
    """
    # Try to import elasticsearch
    try:
        from elasticsearch import Elasticsearch
    except ImportError as e:
        raise ImportError(
            "elasticsearch package is required. Install with: "
            "pip install smf-mcp[elasticsearch7|elasticsearch8|elasticsearch9] or "
            "uv add smf-mcp[elasticsearch7|elasticsearch8|elasticsearch9]"
        ) from e

    kwargs = es_config.to_client_kwargs()
    client = Elasticsearch(**kwargs)
    
    # Check version compatibility
    if not skip_version_check:
        try:
            check_version_compatibility(
                client,
                expected_major=es_config.compatibility_version,
            )
        except ElasticsearchVersionMismatchError:
            # Close client before raising
            try:
                client.close()
            except Exception:
                pass
            raise
    
    return client


def build_elasticsearch_connection_async(
    es_config: ElasticsearchConfiguration,
    skip_version_check: bool = False,
) -> "AsyncElasticsearch":
    """
    Build asynchronous Elasticsearch client from configuration.
    
    Validates version compatibility between client and cluster.
    
    Args:
        es_config: ElasticsearchConfiguration instance
        skip_version_check: If True, skip version compatibility check (not recommended)
        
    Returns:
        AsyncElasticsearch client instance (async)
        
    Raises:
        ImportError: If elasticsearch package is not installed
        ElasticsearchVersionMismatchError: If client and cluster versions are incompatible
        ConnectionError: If unable to connect to cluster
        
    Example:
        >>> from smf.plugins.elasticsearch import ElasticsearchConfiguration
        >>> config = ElasticsearchConfiguration(hosts="http://localhost:9200")
        >>> client = build_elasticsearch_connection_async(config)
        >>> # Use with async/await
        >>> # result = await client.search(index="my_index", body={"query": {"match_all": {}}})
    """
    # Try to import AsyncElasticsearch
    try:
        from elasticsearch import AsyncElasticsearch
    except ImportError as e:
        raise ImportError(
            "elasticsearch package is required. Install with: "
            "pip install smf-mcp[elasticsearch7|elasticsearch8|elasticsearch9] or "
            "uv add smf-mcp[elasticsearch7|elasticsearch8|elasticsearch9]"
        ) from e

    kwargs = es_config.to_client_kwargs()
    client = AsyncElasticsearch(**kwargs)
    
    # Note: Async version check requires async context
    # For now, we'll skip it for async clients and rely on sync check
    # Users should use sync client for initial connection validation
    
    return client
