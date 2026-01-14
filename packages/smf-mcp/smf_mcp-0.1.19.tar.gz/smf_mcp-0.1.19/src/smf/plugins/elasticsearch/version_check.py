"""
Elasticsearch Version Compatibility Checking.

Detects cluster version and validates compatibility with client version.
"""

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from elasticsearch import AsyncElasticsearch, Elasticsearch


class ElasticsearchVersionMismatchError(Exception):
    """Raised when client and cluster versions are incompatible."""
    
    def __init__(
        self,
        client_major: int,
        cluster_major: int,
        client_version: str,
        cluster_version: str,
    ):
        self.client_major = client_major
        self.cluster_major = cluster_major
        self.client_version = client_version
        self.cluster_version = cluster_version
        
        message = (
            f"Version mismatch detected: Client {client_major}.x (version {client_version}) "
            f"is not compatible with cluster {cluster_major}.x (version {cluster_version}).\n"
            f"Install the correct client version:\n"
            f"  uv add smf-mcp[elasticsearch{cluster_major}] or\n"
            f"  pip install \"elasticsearch>={cluster_major},<{cluster_major + 1}\""
        )
        super().__init__(message)


def get_client_version() -> Tuple[int, str]:
    """
    Get the major version and full version string of the installed Elasticsearch client.
    
    Returns:
        Tuple of (major_version, full_version_string)
        
    Raises:
        ImportError: If elasticsearch package is not installed
    """
    try:
        import elasticsearch
        version_str = getattr(elasticsearch, "__version__", None)
        if version_str is None:
            # Try alternative attribute
            version_str = getattr(elasticsearch, "__versionstr__", "unknown")
        
        # Extract major version
        major_version = int(version_str.split(".")[0])
        return major_version, version_str
    except ImportError:
        raise ImportError(
            "elasticsearch package is required. Install with: "
            "pip install smf-mcp[elasticsearch7|elasticsearch8|elasticsearch9] or "
            "uv add smf-mcp[elasticsearch7|elasticsearch8|elasticsearch9]"
        )


def get_cluster_version(client: "Elasticsearch") -> Tuple[int, str]:
    """
    Get the major version and full version string of the Elasticsearch cluster.
    
    Args:
        client: Elasticsearch client instance
        
    Returns:
        Tuple of (major_version, full_version_string)
        
    Raises:
        ConnectionError: If unable to connect to cluster
        ValueError: If version information cannot be parsed
    """
    try:
        # GET / returns cluster info including version
        info = client.info()
        
        # Extract version from response
        version_str = info.get("version", {}).get("number", "unknown")
        
        # Extract major version
        try:
            major_version = int(version_str.split(".")[0])
        except (ValueError, IndexError):
            raise ValueError(f"Unable to parse cluster version: {version_str}")
        
        return major_version, version_str
    except Exception as e:
        raise ConnectionError(
            f"Failed to retrieve cluster version information: {e}. "
            "Make sure Elasticsearch is running and accessible."
        ) from e


def check_version_compatibility(
    client: "Elasticsearch",
    expected_major: int = None,
    skip_check: bool = False,
) -> None:
    """
    Check compatibility between client and cluster versions.
    
    Args:
        client: Elasticsearch client instance
        expected_major: Expected major version (from config). If None, uses client version.
        skip_check: If True, skip version check (not recommended)
        
    Raises:
        ElasticsearchVersionMismatchError: If versions are incompatible
        ImportError: If elasticsearch package is not installed
        ConnectionError: If unable to connect to cluster
    """
    if skip_check:
        return
    
    # Get client version
    client_major, client_version = get_client_version()
    
    # Get cluster version
    cluster_major, cluster_version = get_cluster_version(client)
    
    # Check if client and cluster versions match
    if client_major != cluster_major:
        raise ElasticsearchVersionMismatchError(
            client_major=client_major,
            cluster_major=cluster_major,
            client_version=client_version,
            cluster_version=cluster_version,
        )
    
    # If expected_major is set, validate it matches cluster version
    if expected_major is not None and expected_major != cluster_major:
        import warnings
        warnings.warn(
            f"Configuration specifies compatibility_version={expected_major}, "
            f"but cluster is running version {cluster_major}.x ({cluster_version}). "
            f"Consider updating ELASTICSEARCH_COMPATIBILITY_VERSION to {cluster_major}.",
            UserWarning,
        )
