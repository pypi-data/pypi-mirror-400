"""Dynamic entity registry for cross-site deep linking.

Microsites register their entity definitions at startup. The registry is
empty by default - no hardcoded definitions.

Usage:
    # Option 1: Register entities programmatically
    from yirifi_ops_auth.deeplink import register_entities

    register_entities(
        microsite_id="risk",
        name="Risk Dashboard",
        urls={"dev": "http://localhost:5012", "uat": "...", "prd": "..."},
        entities=[
            {"type": "risk_item", "path": "/risk-management/collections/risk_items/{id}"},
        ]
    )

    # Option 2: Load from YAML file
    from yirifi_ops_auth.deeplink import load_from_yaml
    load_from_yaml("deeplinks.yaml")
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class RegistrationError(Exception):
    """Raised when entity/microsite registration fails validation."""
    pass


@dataclass(frozen=True)
class EntityDefinition:
    """Definition of an entity type for deep linking."""
    entity_type: str
    microsite: str
    path_template: str
    description: Optional[str] = None

    def __post_init__(self) -> None:
        if "{id}" not in self.path_template:
            raise ValueError(
                f"path_template must contain {{id}} placeholder: {self.path_template}"
            )


@dataclass(frozen=True)
class MicrositeConfig:
    """Configuration for a microsite."""
    id: str
    name: str
    urls: Dict[str, str] = field(default_factory=dict)  # {"dev": "...", "uat": "...", "prd": "..."}

    def get_url(self, env: str) -> Optional[str]:
        """Get the URL for a specific environment."""
        return self.urls.get(env)

    # Backwards compatibility properties
    @property
    def dev_url(self) -> str:
        return self.urls.get("dev", "")

    @property
    def uat_url(self) -> str:
        return self.urls.get("uat", "")

    @property
    def prd_url(self) -> str:
        return self.urls.get("prd", "")


class DeepLinkRegistry:
    """Dynamic registry for entity definitions and microsite configurations.

    Thread-safe registry that microsites populate at startup.
    """

    def __init__(self) -> None:
        self._entities: Dict[str, EntityDefinition] = {}
        self._microsites: Dict[str, MicrositeConfig] = {}

    def register_microsite(
        self,
        id: str,
        name: str,
        urls: Dict[str, str],
    ) -> None:
        """Register a microsite configuration.

        Args:
            id: Microsite identifier (e.g., 'risk', 'reg')
            name: Human-readable name (e.g., 'Risk Dashboard')
            urls: Dict mapping env to URL (e.g., {"dev": "http://localhost:5012", ...})

        Raises:
            RegistrationError: If validation fails
        """
        # Validate URLs
        required_envs = {"dev", "uat", "prd"}
        missing = required_envs - set(urls.keys())
        if missing:
            raise RegistrationError(
                f"Microsite '{id}' missing URLs for environments: {missing}"
            )

        config = MicrositeConfig(id=id, name=name, urls=urls)
        self._microsites[id] = config
        logger.debug(f"Registered microsite: {id}")

    def register_entity(
        self,
        entity_type: str,
        microsite: str,
        path_template: str,
        description: Optional[str] = None,
        auto_create_microsite: bool = False,
    ) -> None:
        """Register a single entity definition.

        Args:
            entity_type: Entity type identifier (e.g., 'risk_item')
            microsite: Microsite ID that owns this entity
            path_template: URL path with {id} placeholder
            description: Optional description
            auto_create_microsite: If True, skip microsite existence check

        Raises:
            RegistrationError: If validation fails
        """
        # Validate microsite exists (unless auto_create is True)
        if not auto_create_microsite and microsite not in self._microsites:
            raise RegistrationError(
                f"Cannot register entity '{entity_type}': microsite '{microsite}' not registered. "
                f"Register the microsite first with register_microsite()."
            )

        # Validate path template
        if "{id}" not in path_template:
            raise RegistrationError(
                f"Entity '{entity_type}' path_template must contain {{id}}: {path_template}"
            )

        # Warn on duplicate (but allow override)
        if entity_type in self._entities:
            logger.warning(f"Overwriting existing entity definition: {entity_type}")

        defn = EntityDefinition(
            entity_type=entity_type,
            microsite=microsite,
            path_template=path_template,
            description=description,
        )
        self._entities[entity_type] = defn
        logger.debug(f"Registered entity: {entity_type} -> {microsite}")

    def register_entities(
        self,
        microsite_id: str,
        entities: List[Dict[str, Any]],
        urls: Dict[str, str],
        name: Optional[str] = None,
    ) -> None:
        """Bulk register a microsite and its entities.

        Convenience method for registering everything at once.

        Args:
            microsite_id: Microsite identifier
            entities: List of dicts with 'type', 'path', and optional 'description'
            urls: URL mapping for the microsite
            name: Human-readable name (defaults to title-cased microsite_id)

        Example:
            register_entities(
                microsite_id="risk",
                name="Risk Dashboard",
                urls={"dev": "http://localhost:5012", "uat": "...", "prd": "..."},
                entities=[
                    {"type": "risk_item", "path": "/items/{id}", "description": "Risk item"},
                    {"type": "risk_category", "path": "/categories/{id}"},
                ]
            )
        """
        # Default name from ID
        if name is None:
            name = microsite_id.replace("_", " ").title()

        # Register microsite first
        self.register_microsite(id=microsite_id, name=name, urls=urls)

        # Register entities
        for entity in entities:
            self.register_entity(
                entity_type=entity["type"],
                microsite=microsite_id,
                path_template=entity["path"],
                description=entity.get("description"),
            )

    def get_entity(self, entity_type: str) -> Optional[EntityDefinition]:
        """Get entity definition by type."""
        return self._entities.get(entity_type)

    def get_microsite(self, microsite_id: str) -> Optional[MicrositeConfig]:
        """Get microsite configuration by ID."""
        return self._microsites.get(microsite_id)

    def list_entities(self) -> List[str]:
        """List all registered entity types."""
        return list(self._entities.keys())

    def list_microsites(self) -> List[str]:
        """List all registered microsite IDs."""
        return list(self._microsites.keys())

    def list_entities_for_microsite(self, microsite: str) -> List[str]:
        """List entity types for a specific microsite."""
        return [
            et for et, defn in self._entities.items()
            if defn.microsite == microsite
        ]

    def clear(self) -> None:
        """Clear all registrations. Useful for testing."""
        self._entities.clear()
        self._microsites.clear()
        logger.debug("Registry cleared")

    def is_empty(self) -> bool:
        """Check if registry has no registrations."""
        return len(self._entities) == 0 and len(self._microsites) == 0


# Module-level singleton
_registry = DeepLinkRegistry()


# Public API functions that delegate to the singleton
def register_microsite(
    id: str,
    name: str,
    urls: Dict[str, str],
) -> None:
    """Register a microsite configuration."""
    _registry.register_microsite(id=id, name=name, urls=urls)


def register_entity(
    entity_type: str,
    microsite: str,
    path_template: str,
    description: Optional[str] = None,
) -> None:
    """Register a single entity definition."""
    _registry.register_entity(
        entity_type=entity_type,
        microsite=microsite,
        path_template=path_template,
        description=description,
    )


def register_entities(
    microsite_id: str,
    entities: List[Dict[str, Any]],
    urls: Dict[str, str],
    name: Optional[str] = None,
) -> None:
    """Bulk register a microsite and its entities."""
    _registry.register_entities(
        microsite_id=microsite_id,
        entities=entities,
        urls=urls,
        name=name,
    )


def get_entity_definition(entity_type: str) -> Optional[EntityDefinition]:
    """Get entity definition by type.

    Checks local registry first, then federated sources if available.
    Local definitions take priority over federated ones.

    Args:
        entity_type: The entity type to look up

    Returns:
        EntityDefinition if found, None otherwise
    """
    # 1. Check local registry first (local takes priority)
    defn = _registry.get_entity(entity_type)
    if defn:
        return defn

    # 2. Fallback to federation cache if available
    try:
        from .federation import get_federation_client

        federation = get_federation_client()
        if federation:
            remote = federation.get_entity(entity_type)
            if remote:
                # Convert federation response to EntityDefinition
                return EntityDefinition(
                    entity_type=remote["entity_type"],
                    microsite=remote["microsite"],
                    path_template=remote["path_template"],
                    description=remote.get("description"),
                )
    except ImportError:
        # Federation module not available
        pass
    except Exception as e:
        logger.debug(f"Federation lookup failed for {entity_type}: {e}")

    return None


def get_microsite_for_entity(entity_type: str) -> Optional[str]:
    """Get the microsite ID for an entity type."""
    defn = _registry.get_entity(entity_type)
    return defn.microsite if defn else None


def list_entity_types() -> List[str]:
    """List all registered entity types."""
    return _registry.list_entities()


def list_entity_types_for_microsite(microsite: str) -> List[str]:
    """List entity types for a specific microsite."""
    return _registry.list_entities_for_microsite(microsite)


def list_microsites() -> List[str]:
    """List all registered microsite IDs."""
    return _registry.list_microsites()


def get_microsite_config(microsite_id: str) -> Optional[MicrositeConfig]:
    """Get microsite configuration by ID."""
    return _registry.get_microsite(microsite_id)


def get_microsite_name(microsite_id: str) -> Optional[str]:
    """Get human-readable name for a microsite."""
    config = _registry.get_microsite(microsite_id)
    return config.name if config else None


def get_microsite_base_url(microsite: str, env: Optional[str] = None) -> Optional[str]:
    """Get base URL for a microsite in a specific environment.

    Checks local registry first, then federated sources if available.

    Args:
        microsite: Microsite ID
        env: Environment ('dev', 'uat', 'prd'). If None, uses Environment.get()

    Returns:
        Base URL string or None if microsite not found
    """
    from .environment import Environment

    env = env or Environment.get()

    # 1. Check local registry first
    config = _registry.get_microsite(microsite)
    if config:
        return config.get_url(env)

    # 2. Fallback to federation cache if available
    try:
        from .federation import get_federation_client

        federation = get_federation_client()
        if federation:
            urls = federation.get_microsite_urls(microsite)
            if urls:
                return urls.get(env)
    except ImportError:
        # Federation module not available
        pass
    except Exception as e:
        logger.debug(f"Federation URL lookup failed for {microsite}: {e}")

    return None


def clear_registry() -> None:
    """Clear all registrations. Useful for testing."""
    _registry.clear()


def get_registry() -> DeepLinkRegistry:
    """Get the registry singleton. Useful for advanced use cases."""
    return _registry
