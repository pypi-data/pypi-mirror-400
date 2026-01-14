"""
Helpers pour simplifier l'authentification et l'autorisation.

Ces helpers permettent d'utiliser facilement les claims et les permissions
dans les outils sans avoir à gérer manuellement l'extraction.
"""

from typing import Any, Dict, List, Optional, Union
from functools import wraps


def get_current_user(arguments: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Obtenir les claims de l'utilisateur actuel depuis les arguments.
    
    Cette fonction extrait automatiquement les claims depuis les arguments
    de l'outil, peu importe comment ils ont été injectés.
    
    Args:
        arguments: Arguments de l'outil (peut être None, les claims seront extraits automatiquement)
        
    Returns:
        Claims de l'utilisateur ou None si non authentifié
        
    Example:
        ```python
        @mcp.tool
        def my_tool(name: str, claims: dict = None) -> dict:
            user = get_current_user(claims)
            if not user:
                return {"error": "Not authenticated"}
            return {"message": f"Hello {user['username']}"}
        ```
    """
    if arguments is None:
        return None
    
    # Si c'est déjà un dict de claims, le retourner
    if isinstance(arguments, dict):
        # Vérifier si c'est directement les claims (pas les arguments)
        if "sub" in arguments or "user_id" in arguments or "username" in arguments:
            return arguments
    
    # Extraire depuis le contexte SMF
    if isinstance(arguments, dict):
        # Méthode 1: Depuis _smf_context
        smf_context = arguments.get("_smf_context")
        if isinstance(smf_context, dict):
            claims = smf_context.get("claims") or smf_context.get("auth")
            if claims:
                return claims
        
        # Méthode 2: Depuis les clés directes
        for key in ("_smf_claims", "_auth_claims", "_claims", "claims", "auth"):
            if key in arguments:
                value = arguments[key]
                if isinstance(value, dict) and (value.get("sub") or value.get("user_id") or value.get("username")):
                    return value
    
    return None


def require_auth(func: Optional[Any] = None, *, error_message: str = "Authentication required"):
    """
    Décorateur pour exiger une authentification.
    
    Args:
        func: Fonction à décorer
        error_message: Message d'erreur si non authentifié
        
    Example:
        ```python
        @mcp.tool
        @require_auth
        def protected_tool(name: str, claims: dict = None) -> dict:
            user = get_current_user(claims)
            return {"message": f"Hello {user['username']}"}
        ```
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Chercher les claims dans les arguments
            claims = None
            for arg in args:
                if isinstance(arg, dict) and (arg.get("sub") or arg.get("user_id")):
                    claims = arg
                    break
            if not claims:
                claims = kwargs.get("claims") or kwargs.get("_smf_claims") or kwargs.get("_auth_claims")
            
            if not claims:
                return {"error": error_message}
            
            return f(*args, **kwargs)
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)


def require_role(*roles: str, error_message: Optional[str] = None):
    """
    Décorateur pour exiger un ou plusieurs rôles.
    
    Args:
        *roles: Rôles requis (l'utilisateur doit avoir au moins un de ces rôles)
        error_message: Message d'erreur personnalisé
        
    Example:
        ```python
        @mcp.tool
        @require_role("admin", "moderator")
        def admin_tool(claims: dict = None) -> dict:
            return {"message": "Admin access granted"}
        ```
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extraire les claims
            claims = None
            for arg in args:
                if isinstance(arg, dict) and (arg.get("sub") or arg.get("user_id")):
                    claims = arg
                    break
            if not claims:
                claims = kwargs.get("claims") or kwargs.get("_smf_claims") or kwargs.get("_auth_claims")
            
            if not claims:
                msg = error_message or "Authentication required"
                return {"error": msg}
            
            # Extraire les rôles
            user_roles = claims.get("roles", [])
            if isinstance(user_roles, str):
                user_roles = [user_roles]
            
            # Vérifier si l'utilisateur a au moins un des rôles requis
            if not any(role in user_roles for role in roles):
                msg = error_message or f"Required role: {', '.join(roles)}"
                return {"error": msg}
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission: str, error_message: Optional[str] = None):
    """
    Décorateur pour exiger une permission spécifique.
    
    Args:
        permission: Permission requise (ex: "read:users", "write:index")
        error_message: Message d'erreur personnalisé
        
    Example:
        ```python
        @mcp.tool
        @require_permission("read:users")
        def list_users(claims: dict = None) -> dict:
            return {"users": [...]}
        ```
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extraire les claims
            claims = None
            for arg in args:
                if isinstance(arg, dict) and (arg.get("sub") or arg.get("user_id")):
                    claims = arg
                    break
            if not claims:
                claims = kwargs.get("claims") or kwargs.get("_smf_claims") or kwargs.get("_auth_claims")
            
            if not claims:
                msg = error_message or "Authentication required"
                return {"error": msg}
            
            # Vérifier les permissions
            permissions = claims.get("permissions", [])
            if isinstance(permissions, str):
                permissions = [permissions]
            
            # Support pour les permissions Elasticsearch
            es_perms = claims.get("elasticsearch_permissions", {})
            if es_perms:
                index_names = es_perms.get("index_names", [])
                # Si la permission est pour un index spécifique
                if permission.startswith("index:") and "*" not in index_names:
                    index_name = permission.split(":", 1)[1]
                    if index_name not in index_names:
                        msg = error_message or f"Access denied to index: {index_name}"
                        return {"error": msg}
                elif permission.startswith("index:"):
                    # Admin a accès à tout
                    pass
            
            # Vérifier la permission standard
            if permission not in permissions and "*" not in permissions:
                msg = error_message or f"Required permission: {permission}"
                return {"error": msg}
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_user_id(claims: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Obtenir l'ID de l'utilisateur depuis les claims."""
    if not claims:
        return None
    return claims.get("sub") or claims.get("user_id") or claims.get("username")


def get_user_roles(claims: Optional[Dict[str, Any]] = None) -> List[str]:
    """Obtenir les rôles de l'utilisateur depuis les claims."""
    if not claims:
        return []
    roles = claims.get("roles", [])
    if isinstance(roles, str):
        return [roles]
    return roles if isinstance(roles, list) else []


def has_role(claims: Optional[Dict[str, Any]], role: str) -> bool:
    """Vérifier si l'utilisateur a un rôle spécifique."""
    return role in get_user_roles(claims)


def get_accessible_indices(claims: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Obtenir les index Elasticsearch accessibles à l'utilisateur.
    
    Returns:
        Liste des noms d'index accessibles, ou ["*"] si l'utilisateur a accès à tout
    """
    if not claims:
        return []
    
    es_perms = claims.get("elasticsearch_permissions", {})
    if not es_perms:
        return []
    
    index_names = es_perms.get("index_names", [])
    if "*" in index_names or not index_names:
        return ["*"]
    
    return index_names if isinstance(index_names, list) else [index_names]


def can_access_index(claims: Optional[Dict[str, Any]], index_name: str) -> bool:
    """Vérifier si l'utilisateur peut accéder à un index spécifique."""
    accessible = get_accessible_indices(claims)
    return "*" in accessible or index_name in accessible

