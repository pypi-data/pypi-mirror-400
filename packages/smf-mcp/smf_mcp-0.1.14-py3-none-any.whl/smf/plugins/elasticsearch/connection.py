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


def build_elasticsearch_connection(
    es_config: ElasticsearchConfiguration,
) -> "Elasticsearch":
    """
    Build synchronous Elasticsearch client from configuration.
    
    Args:
        es_config: ElasticsearchConfiguration instance
        
    Returns:
        Elasticsearch client instance (sync)
        
    Raises:
        ImportError: If elasticsearch package is not installed
        
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
            "pip install smf-mcp[elasticsearch] or uv add smf-mcp[elasticsearch]"
        ) from e

    kwargs = es_config.to_client_kwargs()
    return Elasticsearch(**kwargs)


def build_elasticsearch_connection_async(
    es_config: ElasticsearchConfiguration,
) -> "AsyncElasticsearch":
    """
    Build asynchronous Elasticsearch client from configuration.
    
    Args:
        es_config: ElasticsearchConfiguration instance
        
    Returns:
        AsyncElasticsearch client instance (async)
        
    Raises:
        ImportError: If elasticsearch package is not installed
        
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
            "pip install smf-mcp[elasticsearch] or uv add smf-mcp[elasticsearch]"
        ) from e

    kwargs = es_config.to_client_kwargs()
    return AsyncElasticsearch(**kwargs)
