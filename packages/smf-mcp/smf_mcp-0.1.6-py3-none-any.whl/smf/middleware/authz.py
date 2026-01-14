"""
Authorization middleware for SMF.

This middleware:
1. Extracts claims from FastMCP authentication context
2. Injects claims into tool arguments automatically
3. Performs authorization checks
"""

from typing import Any, Dict, Optional
import contextvars

from fastmcp import FastMCP

from smf.settings import Settings
from smf.utils.import_tools import load_callable

# Context variable pour stocker les claims de la requête actuelle
_current_claims: contextvars.ContextVar[Optional[Dict[str, Any]]] = contextvars.ContextVar(
    "_current_claims", default=None
)


class AuthorizationError(Exception):
    """Authorization failed."""


def get_current_claims() -> Optional[Dict[str, Any]]:
    """
    Obtenir les claims de l'utilisateur actuel depuis le contexte.
    
    Cette fonction peut être utilisée dans les outils pour accéder aux claims
    sans avoir à les passer en paramètre.
    
    Returns:
        Claims de l'utilisateur ou None
    """
    return _current_claims.get()


def _extract_claims_from_fastmcp(mcp: FastMCP) -> Optional[Dict[str, Any]]:
    """
    Extraire les claims depuis le contexte FastMCP.
    
    FastMCP stocke les claims validés dans le contexte de la requête.
    """
    # Essayer différentes méthodes pour obtenir les claims depuis FastMCP
    # Cela dépend de l'implémentation de FastMCP
    
    # Méthode 1: Depuis request.state (si disponible)
    if hasattr(mcp, "_request_context"):
        request_context = getattr(mcp, "_request_context", None)
        if request_context:
            if hasattr(request_context, "state"):
                state = request_context.state
                if hasattr(state, "claims"):
                    return state.claims
                if hasattr(state, "user"):
                    return state.user
    
    # Méthode 2: Depuis les attributs du serveur (si FastMCP les stocke)
    if hasattr(mcp, "_current_user"):
        return getattr(mcp, "_current_user")
    
    return None


def _extract_claims(arguments: Dict[str, Any]) -> Optional[Any]:
    """
    Extraire les claims depuis les arguments de l'outil.
    
    Vérifie plusieurs emplacements où les claims peuvent être stockés.
    """
    # Méthode 1: Depuis le contexte SMF
    if "_smf_context" in arguments and isinstance(arguments["_smf_context"], dict):
        context = arguments["_smf_context"]
        if "claims" in context:
            return context["claims"]
        if "auth" in context:
            return context["auth"]

    # Méthode 2: Depuis les clés directes
    for key in ("_smf_claims", "_auth_claims", "_claims", "claims", "auth"):
        if key in arguments:
            value = arguments[key]
            if isinstance(value, dict):
                return value

    return None


def _inject_claims(arguments: Dict[str, Any], claims: Optional[Dict[str, Any]]) -> None:
    """
    Injecter les claims dans les arguments de l'outil.
    
    Les claims sont injectés sous plusieurs clés pour compatibilité maximale.
    """
    if not claims:
        return
    
    # Ne pas écraser si déjà présent
    if "_smf_claims" not in arguments:
        arguments["_smf_claims"] = claims
    if "_auth_claims" not in arguments:
        arguments["_auth_claims"] = claims
    if "claims" not in arguments:
        arguments["claims"] = claims
    
    # Créer ou mettre à jour le contexte SMF
    if "_smf_context" not in arguments:
        arguments["_smf_context"] = {}
    if not isinstance(arguments["_smf_context"], dict):
        arguments["_smf_context"] = {}
    
    arguments["_smf_context"]["claims"] = claims
    arguments["_smf_context"]["auth"] = claims


def _call_provider(provider, claims, resource, action, context, settings) -> bool:
    try:
        return bool(
            provider(
                claims=claims,
                resource=resource,
                action=action,
                context=context,
                settings=settings,
            )
        )
    except TypeError:
        return bool(provider(claims, resource, action))


def attach_authorization(mcp: FastMCP, settings: Settings) -> None:
    """
    Attacher le middleware d'autorisation avec injection automatique des claims.
    
    Ce middleware :
    1. Extrait les claims depuis FastMCP (après validation JWT/auth)
    2. Injecte automatiquement les claims dans les arguments des outils
    3. Vérifie les autorisations si enable_authz est activé
    """
    # Toujours injecter les claims si l'authentification est activée
    inject_claims = settings.auth_provider and settings.auth_provider.value != "none"
    
    # Charger le provider d'autorisation si nécessaire
    provider = None
    if settings.enable_authz:
        if not settings.authz_provider:
            raise ValueError("Authorization enabled but no authz_provider configured")
        provider = load_callable(settings.authz_provider)

    if hasattr(mcp, "on_call_tool"):
        original_call_tool = getattr(mcp, "on_call_tool", None)

        def authorize_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Any:
            # Étape 1: Extraire les claims depuis FastMCP ou les arguments
            claims = _extract_claims_from_fastmcp(mcp) or _extract_claims(arguments)
            
            # Étape 2: Stocker dans le contexte pour get_current_claims()
            if claims:
                _current_claims.set(claims)
            
            # Étape 3: Injecter les claims dans les arguments (si auth activée)
            if inject_claims and claims:
                _inject_claims(arguments, claims)
            
            # Étape 4: Vérifier l'autorisation (si activée)
            if provider:
                allowed = _call_provider(
                    provider,
                    claims,
                    tool_name,
                    "call",
                    {"type": "tool", "arguments": arguments},
                    settings,
                )
                if not allowed:
                    raise AuthorizationError(f"Unauthorized tool call: {tool_name}")
            
            # Étape 5: Appeler l'outil original
            try:
                return original_call_tool(tool_name, arguments) if original_call_tool else None
            finally:
                # Nettoyer le contexte
                _current_claims.set(None)

        mcp.on_call_tool = authorize_tool_call

    if hasattr(mcp, "on_read_resource"):
        original_read_resource = getattr(mcp, "on_read_resource", None)

        def authorize_resource_read(resource_uri: str) -> Any:
            # Extraire les claims pour les ressources aussi
            claims = _extract_claims_from_fastmcp(mcp)
            if claims:
                _current_claims.set(claims)
            
            # Vérifier l'autorisation pour les ressources
            if provider:
                allowed = _call_provider(
                    provider,
                    claims,
                    resource_uri,
                    "read",
                    {"type": "resource"},
                    settings,
                )
                if not allowed:
                    raise AuthorizationError(f"Unauthorized resource read: {resource_uri}")
            
            try:
                return original_read_resource(resource_uri) if original_read_resource else None
            finally:
                _current_claims.set(None)

        mcp.on_read_resource = authorize_resource_read
