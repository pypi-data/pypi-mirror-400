"""Deep link resolution - generates URLs to entities across microsites.

Core functions:
- resolve_link(): Generate a URL for an entity
- deep_link_info(): Get URL + accessibility info for permission-aware rendering
"""

from dataclasses import dataclass
from typing import Optional, Any
from urllib.parse import urlencode, quote

from .registry import (
    get_entity_definition,
    get_microsite_base_url,
    get_microsite_name,
)


@dataclass
class DeepLinkInfo:
    """Information about a deep link including accessibility.

    Attributes:
        url: The resolved URL to the entity
        accessible: Whether the current user can access the target microsite
        microsite: The target microsite ID
        microsite_name: Human-readable name of the target microsite
        entity_type: The entity type that was resolved
        entity_id: The entity ID used in resolution
    """
    url: str
    accessible: bool
    microsite: str
    microsite_name: str
    entity_type: str
    entity_id: str


class DeepLinkError(Exception):
    """Raised when deep link resolution fails."""
    pass


class UnknownEntityTypeError(DeepLinkError):
    """Raised when an unknown entity type is provided."""
    pass


class UnknownMicrositeError(DeepLinkError):
    """Raised when a microsite URL cannot be resolved."""
    pass


def resolve_link(
    entity_type: str,
    entity_id: Any,
    env: Optional[str] = None,
    query_params: Optional[dict] = None,
) -> str:
    """Resolve a deep link URL for an entity.

    Args:
        entity_type: The type of entity (e.g., 'risk_item', 'user')
        entity_id: The entity's identifier (will be converted to string)
        env: Environment ('dev', 'uat', 'prd'). If None, uses current environment.
        query_params: Optional query parameters to append to URL

    Returns:
        Full URL to the entity

    Raises:
        UnknownEntityTypeError: If entity_type is not in the registry
        UnknownMicrositeError: If microsite URL cannot be resolved

    Example:
        >>> resolve_link('risk_item', 'r_yid_123')
        'http://localhost:5012/risk-management/collections/risk_items/r_yid_123'

        >>> resolve_link('user', 42, query_params={'tab': 'permissions'})
        'http://localhost:5013/users/42?tab=permissions'
    """
    # Get entity definition
    defn = get_entity_definition(entity_type)
    if not defn:
        raise UnknownEntityTypeError(f"Unknown entity type: {entity_type}")

    # Get base URL for the microsite
    base_url = get_microsite_base_url(defn.microsite, env)
    if not base_url:
        raise UnknownMicrositeError(f"No URL configured for microsite: {defn.microsite}")

    # Build the path with entity ID
    entity_id_str = str(entity_id)
    path = defn.path_template.format(id=quote(entity_id_str, safe=''))

    # Construct full URL
    url = f"{base_url.rstrip('/')}{path}"

    # Add query parameters if provided
    if query_params:
        url = f"{url}?{urlencode(query_params)}"

    return url


def deep_link_info(
    entity_type: str,
    entity_id: Any,
    user: Optional[Any] = None,
    env: Optional[str] = None,
    query_params: Optional[dict] = None,
) -> DeepLinkInfo:
    """Get deep link information including accessibility status.

    This is the preferred function for permission-aware rendering.
    It returns all information needed to render either an active link
    or a disabled placeholder.

    Args:
        entity_type: The type of entity (e.g., 'risk_item', 'user')
        entity_id: The entity's identifier
        user: AuthUser object (from g.current_user) for access checking.
              If None, accessible defaults to True.
        env: Environment. If None, uses current environment.
        query_params: Optional query parameters

    Returns:
        DeepLinkInfo with url, accessibility, and metadata

    Raises:
        UnknownEntityTypeError: If entity_type is not in the registry

    Example:
        >>> info = deep_link_info('risk_item', 'r_yid_123', g.current_user)
        >>> if info.accessible:
        ...     print(f'<a href="{info.url}">Open in {info.microsite_name}</a>')
        ... else:
        ...     print(f'<span title="No access">{info.microsite_name}</span>')
    """
    # Get entity definition
    defn = get_entity_definition(entity_type)
    if not defn:
        raise UnknownEntityTypeError(f"Unknown entity type: {entity_type}")

    # Resolve the URL
    url = resolve_link(entity_type, entity_id, env, query_params)

    # Check accessibility
    accessible = True
    if user is not None:
        # Use the auth client's has_access_to method
        if hasattr(user, 'has_access_to'):
            accessible = user.has_access_to(defn.microsite)
        elif hasattr(user, 'microsites'):
            # Fallback: check microsites list
            accessible = defn.microsite in (user.microsites or [])

    return DeepLinkInfo(
        url=url,
        accessible=accessible,
        microsite=defn.microsite,
        microsite_name=get_microsite_name(defn.microsite) or defn.microsite.title(),
        entity_type=entity_type,
        entity_id=str(entity_id),
    )


def can_link_to(entity_type: str, user: Optional[Any] = None) -> bool:
    """Check if a user can access the microsite for an entity type.

    Useful for conditionally showing cross-link UI elements.

    Args:
        entity_type: The type of entity
        user: AuthUser object for access checking

    Returns:
        True if user can access the target microsite, False otherwise
    """
    defn = get_entity_definition(entity_type)
    if not defn:
        return False

    if user is None:
        return True

    if hasattr(user, 'has_access_to'):
        return user.has_access_to(defn.microsite)
    elif hasattr(user, 'microsites'):
        return defn.microsite in (user.microsites or [])

    return True


def get_entity_microsite_name(entity_type: str) -> Optional[str]:
    """Get the display name of the microsite for an entity type.

    Args:
        entity_type: The type of entity

    Returns:
        Human-readable microsite name, or None if entity type unknown
    """
    defn = get_entity_definition(entity_type)
    if not defn:
        return None
    return get_microsite_name(defn.microsite) or defn.microsite.title()
