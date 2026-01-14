"""Deep linking module for cross-microsite navigation.

This module provides tools to generate URLs to entities across different
Yirifi Ops microsites with permission-aware rendering.

Quick Start:
    1. Register your microsite's entities:
        from yirifi_ops_auth.deeplink import register_entities

        register_entities(
            microsite_id="risk",
            name="Risk Dashboard",
            urls={"dev": "http://localhost:5012", "uat": "...", "prd": "..."},
            entities=[
                {"type": "risk_item", "path": "/items/{id}"},
            ]
        )

    2. Set up in your Flask app:
        from yirifi_ops_auth.deeplink import setup_deeplinks
        setup_deeplinks(app, env='dev')

    3. Use in templates:
        {{ cross_link('risk_item', item.r_yid, 'Open in Risk Dashboard') }}

    4. Or use in Python:
        from yirifi_ops_auth.deeplink import resolve_link
        url = resolve_link('risk_item', 'r_yid_123')

Federation (v3.1.0+):
    Enable cross-microsite entity discovery without manual registration:

        setup_deeplinks(
            app,
            env='dev',
            enable_federation=True,  # Queries auth service + microsites
            expose_references=True,  # Exposes /api/v1/references
        )

    Now templates can use entities from ANY microsite:
        {{ cross_link('reg_link', link.id) }}  # Works without registering!

Registration Functions:
    - register_entities: Register a microsite and its entities (bulk)
    - register_microsite: Register a microsite configuration
    - register_entity: Register a single entity definition
    - load_from_yaml: Load entity definitions from YAML file
    - clear_registry: Clear all registrations (for testing)

Resolution Functions:
    - setup_deeplinks: Initialize deep linking for a Flask app
    - resolve_link: Generate a URL for an entity
    - deep_link_info: Get URL + accessibility info
    - can_link_to: Check if user can access an entity's microsite

Template Helpers (available after setup_deeplinks):
    - {{ deep_link(entity_type, entity_id) }} - Returns URL string
    - {{ deep_link_info(entity_type, entity_id) }} - Returns DeepLinkInfo object
    - {{ cross_link(entity_type, entity_id, label) }} - Renders permission-aware link
    - {{ cross_link_button(entity_type, entity_id, label) }} - Renders styled button

Registry Query Functions:
    - get_entity_definition: Get definition for an entity type
    - list_entity_types: List all registered entity types
    - list_entity_types_for_microsite: List entity types for a microsite
    - list_microsites: List all registered microsites

Federation Functions:
    - configure_federation: Configure and start federation client
    - get_federation_client: Get the federation client singleton
    - stop_federation: Stop the federation client
    - FederationConfig: Configuration dataclass for federation

Environment:
    - Environment: Thread-safe environment class with get/set/override
    - get_environment: Get current environment (dev/uat/prd)
    - set_environment: Explicitly set environment
"""

# Flask integration
from .jinja import setup_deeplinks

# Core resolution
from .resolver import (
    resolve_link,
    deep_link_info,
    can_link_to,
    get_entity_microsite_name,
    DeepLinkInfo,
    DeepLinkError,
    UnknownEntityTypeError,
    UnknownMicrositeError,
)

# Registry - registration functions
from .registry import (
    register_entities,
    register_microsite,
    register_entity,
    clear_registry,
    get_registry,
    # Query functions
    get_entity_definition,
    get_microsite_for_entity,
    get_microsite_config,
    get_microsite_name,
    get_microsite_base_url,
    list_entity_types,
    list_entity_types_for_microsite,
    list_microsites,
    # Types
    EntityDefinition,
    MicrositeConfig,
    RegistrationError,
    DeepLinkRegistry,
)

# YAML loading
from .yaml_loader import (
    load_from_yaml,
    load_from_string,
    discover_and_load,
    YamlLoadError,
)

# Environment
from .environment import (
    Environment,
    get_environment,
    set_environment,
    VALID_ENVIRONMENTS,
)

# Federation
from .federation import (
    configure_federation,
    get_federation_client,
    stop_federation,
    clear_federation_cache,
    FederationConfig,
    FederationClient,
    FederationError,
    FederationTimeoutError,
    FederationConnectionError,
)

# Blueprint for /api/v1/references
from .blueprint import references_bp

__all__ = [
    # Flask integration
    'setup_deeplinks',

    # Core resolution
    'resolve_link',
    'deep_link_info',
    'can_link_to',
    'get_entity_microsite_name',
    'DeepLinkInfo',
    'DeepLinkError',
    'UnknownEntityTypeError',
    'UnknownMicrositeError',

    # Registration
    'register_entities',
    'register_microsite',
    'register_entity',
    'clear_registry',
    'get_registry',
    'load_from_yaml',
    'load_from_string',
    'discover_and_load',
    'RegistrationError',
    'YamlLoadError',

    # Registry queries
    'get_entity_definition',
    'get_microsite_for_entity',
    'get_microsite_config',
    'get_microsite_name',
    'get_microsite_base_url',
    'list_entity_types',
    'list_entity_types_for_microsite',
    'list_microsites',

    # Types
    'EntityDefinition',
    'MicrositeConfig',
    'DeepLinkRegistry',

    # Environment
    'Environment',
    'get_environment',
    'set_environment',
    'VALID_ENVIRONMENTS',

    # Federation
    'configure_federation',
    'get_federation_client',
    'stop_federation',
    'clear_federation_cache',
    'FederationConfig',
    'FederationClient',
    'FederationError',
    'FederationTimeoutError',
    'FederationConnectionError',

    # Blueprint
    'references_bp',
]
