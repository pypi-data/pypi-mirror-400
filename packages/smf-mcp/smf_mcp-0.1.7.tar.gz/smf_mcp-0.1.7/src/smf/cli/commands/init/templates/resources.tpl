import json
from datetime import datetime


def get_server_info() -> str:
    """
    Get server information as a resource.
    
    Returns:
        JSON string with server information
    """
    info = {
        "server_name": "My SMF Server",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "tools",
            "resources",
            "prompts"
        ]
    }
    return json.dumps(info, indent=2)


def get_config() -> str:
    """
    Get server configuration.
    
    Returns:
        Configuration information
    """
    return "Server configuration: Production mode, logging enabled, metrics enabled"
