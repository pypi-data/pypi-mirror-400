"""
SMF Middleware - Cross-cutting concerns for MCP servers.

Implements Chain of Responsibility pattern for request/response processing.
"""

from smf.middleware.authz import attach_authorization
from smf.middleware.cache import attach_cache
from smf.middleware.error import attach_error_handling
from smf.middleware.governance import attach_governance
from smf.middleware.logging import attach_logging
from smf.middleware.rate_limit import attach_rate_limiting
from smf.middleware.tracing import attach_tracing

__all__ = [
    "attach_authorization",
    "attach_cache",
    "attach_governance",
    "attach_logging",
    "attach_tracing",
    "attach_rate_limiting",
    "attach_error_handling",
]

