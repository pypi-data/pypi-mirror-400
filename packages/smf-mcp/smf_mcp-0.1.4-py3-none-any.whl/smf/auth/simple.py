"""
Système d'autorisation simple basé sur les rôles et permissions.

Ce module fournit des fonctions d'autorisation prêtes à l'emploi
qui peuvent être utilisées directement dans authz_provider.
"""

from typing import Any, Dict, List, Optional


def simple_role_based_authorize(
    claims: Optional[Dict[str, Any]],
    resource: str,
    action: str,
    context: Optional[Dict[str, Any]] = None,
    settings: Optional[Any] = None,
) -> bool:
    """
    Fonction d'autorisation simple basée sur les rôles.
    
    Règles :
    - Les outils avec préfixe "admin:" nécessitent le rôle "admin"
    - Les outils avec préfixe "public:" sont accessibles à tous les utilisateurs authentifiés
    - Les autres outils nécessitent une authentification
    
    Args:
        claims: Claims de l'utilisateur
        resource: Nom de l'outil ou URI de la ressource
        action: Action ("call" pour les outils, "read" pour les ressources)
        context: Contexte optionnel
        settings: Paramètres SMF
        
    Returns:
        True si autorisé, False sinon
    """
    # Si pas de claims, refuser (sauf si c'est un outil public explicite)
    if not claims:
        return resource.startswith("public:")
    
    # Extraire les rôles
    roles = claims.get("roles", [])
    if isinstance(roles, str):
        roles = [roles]
    
    # Outils admin - nécessitent le rôle "admin"
    if resource.startswith("admin:") or resource.startswith("admin_"):
        return "admin" in roles
    
    # Outils publics - accessibles à tous les utilisateurs authentifiés
    if resource.startswith("public:") or resource.startswith("public_"):
        return True
    
    # Par défaut, autoriser si authentifié
    return True


def elasticsearch_permission_based_authorize(
    claims: Optional[Dict[str, Any]],
    resource: str,
    action: str,
    context: Optional[Dict[str, Any]] = None,
    settings: Optional[Any] = None,
) -> bool:
    """
    Fonction d'autorisation basée sur les permissions Elasticsearch.
    
    Pour les outils Elasticsearch (préfixe "es_"), vérifie que l'utilisateur
    a accès à l'index demandé selon ses permissions Kibana.
    
    Args:
        claims: Claims de l'utilisateur avec permissions Elasticsearch
        resource: Nom de l'outil
        action: Action
        context: Contexte avec les arguments de l'outil
        settings: Paramètres SMF
        
    Returns:
        True si autorisé, False sinon
    """
    # Si pas de claims, refuser
    if not claims:
        return False
    
    # Outils Elasticsearch - vérifier les permissions d'index
    if resource.startswith("es_"):
        # Extraire le nom de l'index depuis les arguments
        index_name = None
        if context and isinstance(context, dict):
            tool_args = context.get("arguments", {})
            index_name = tool_args.get("index_name")
        
        # Si pas d'index spécifique (ex: es_list_indices), autoriser
        if not index_name:
            return True
        
        # Vérifier les permissions Elasticsearch
        es_perms = claims.get("elasticsearch_permissions", {})
        index_names = es_perms.get("index_names", [])
        
        # Admin a accès à tout
        if "*" in index_names:
            return True
        
        # Vérifier si l'index est dans la liste des index accessibles
        return index_name in index_names if isinstance(index_names, list) else False
    
    # Pour les autres outils, utiliser l'autorisation basée sur les rôles
    return simple_role_based_authorize(claims, resource, action, context, settings)


def create_role_based_authorize(
    admin_tools: Optional[List[str]] = None,
    public_tools: Optional[List[str]] = None,
    require_auth: bool = True,
) -> callable:
    """
    Créer une fonction d'autorisation personnalisée basée sur les rôles.
    
    Args:
        admin_tools: Liste des outils nécessitant le rôle "admin"
        public_tools: Liste des outils publics (pas d'auth requise)
        require_auth: Si True, exiger l'authentification pour tous les autres outils
        
    Returns:
        Fonction d'autorisation
        
    Example:
        ```python
        # Dans smf.yaml
        authz_provider: "my_module:my_authorize"
        
        # Dans my_module.py
        from smf.auth.simple import create_role_based_authorize
        
        my_authorize = create_role_based_authorize(
            admin_tools=["delete_user", "manage_index"],
            public_tools=["greet", "info"],
            require_auth=True
        )
        ```
    """
    admin_set = set(admin_tools or [])
    public_set = set(public_tools or [])
    
    def authorize(
        claims: Optional[Dict[str, Any]],
        resource: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        settings: Optional[Any] = None,
    ) -> bool:
        # Outils publics - pas d'auth requise
        if resource in public_set:
            return True
        
        # Si pas de claims et auth requise, refuser
        if not claims:
            return not require_auth
        
        # Extraire les rôles
        roles = claims.get("roles", [])
        if isinstance(roles, str):
            roles = [roles]
        
        # Outils admin - nécessitent le rôle "admin"
        if resource in admin_set:
            return "admin" in roles
        
        # Par défaut, autoriser si authentifié (ou si auth non requise)
        return True if require_auth else True
    
    return authorize

