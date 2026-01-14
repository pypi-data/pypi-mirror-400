"""
SMF Plugins.

Provides integrations and plugins for SMF servers.
"""

from smf.plugins.elasticsearch import (
    create_elasticsearch_tools,
)

__all__ = [
    "create_elasticsearch_tools",
]

