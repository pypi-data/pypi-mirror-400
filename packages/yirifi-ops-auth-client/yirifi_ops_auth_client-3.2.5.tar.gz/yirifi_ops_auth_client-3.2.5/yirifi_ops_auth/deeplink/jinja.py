"""Jinja2 template helpers for deep linking.

Provides template functions and macros for easy cross-site link rendering.

Usage in templates:
    {{ deep_link('risk_item', item.r_yid) }}
    {{ deep_link_info('user', user.id) }}
    {{ cross_link('risk_item', item.r_yid, 'Open in Risk Dashboard') }}
"""

from typing import Any, Optional, List, Dict
from flask import Flask, g, current_app
from markupsafe import Markup

from .resolver import resolve_link, deep_link_info as _deep_link_info, DeepLinkInfo
from .environment import Environment


def get_current_user() -> Optional[Any]:
    """Get the current user from Flask's g context."""
    return getattr(g, 'current_user', None)


def deep_link(
    entity_type: str,
    entity_id: Any,
    query_params: Optional[dict] = None,
) -> str:
    """Jinja2 function to generate a deep link URL.

    Usage:
        <a href="{{ deep_link('risk_item', item.r_yid) }}">View</a>

    Args:
        entity_type: The type of entity (e.g., 'risk_item', 'user')
        entity_id: The entity's identifier
        query_params: Optional query parameters

    Returns:
        URL string
    """
    try:
        return resolve_link(entity_type, entity_id, query_params=query_params)
    except Exception as e:
        current_app.logger.warning(f"Deep link resolution failed: {e}")
        return "#"


def jinja_deep_link_info(
    entity_type: str,
    entity_id: Any,
    query_params: Optional[dict] = None,
) -> DeepLinkInfo:
    """Jinja2 function to get deep link info including accessibility.

    Usage:
        {% set link = deep_link_info('risk_item', item.r_yid) %}
        {% if link.accessible %}
          <a href="{{ link.url }}">{{ link.microsite_name }}</a>
        {% else %}
          <span class="disabled">{{ link.microsite_name }}</span>
        {% endif %}

    Args:
        entity_type: The type of entity
        entity_id: The entity's identifier
        query_params: Optional query parameters

    Returns:
        DeepLinkInfo object with url, accessible, microsite, microsite_name
    """
    user = get_current_user()
    return _deep_link_info(entity_type, entity_id, user=user, query_params=query_params)


def cross_link(
    entity_type: str,
    entity_id: Any,
    label: Optional[str] = None,
    css_class: str = "",
    disabled_class: str = "text-gray-400 cursor-not-allowed",
    icon: bool = True,
    query_params: Optional[dict] = None,
) -> Markup:
    """Jinja2 function to render a permission-aware cross-site link.

    Renders an active link if user has access, or a disabled span if not.

    Usage:
        {{ cross_link('risk_item', item.r_yid, 'Open in Risk Dashboard') }}
        {{ cross_link('user', user.id, icon=False) }}
        {{ cross_link('risk_item', item.r_yid, css_class='btn btn-sm') }}

    Args:
        entity_type: The type of entity
        entity_id: The entity's identifier
        label: Link text. If None, uses microsite name.
        css_class: CSS classes for the link element
        disabled_class: CSS classes when link is disabled
        icon: Whether to show external link icon
        query_params: Optional query parameters

    Returns:
        Markup (safe HTML) for the link or disabled span
    """
    try:
        info = jinja_deep_link_info(entity_type, entity_id, query_params)
    except Exception as e:
        current_app.logger.warning(f"Cross link resolution failed: {e}")
        return Markup(f'<span class="{disabled_class}">Link unavailable</span>')

    link_label = label or f"Open in {info.microsite_name}"
    icon_html = ' <svg class="inline w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>' if icon else ''

    if info.accessible:
        return Markup(
            f'<a href="{info.url}" class="{css_class}" '
            f'target="_blank" rel="noopener noreferrer">'
            f'{link_label}{icon_html}</a>'
        )
    else:
        return Markup(
            f'<span class="{disabled_class}" '
            f'title="No access to {info.microsite_name}">'
            f'{link_label}</span>'
        )


def cross_link_button(
    entity_type: str,
    entity_id: Any,
    label: Optional[str] = None,
    btn_class: str = "inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md",
    active_class: str = "text-blue-600 bg-blue-50 hover:bg-blue-100",
    disabled_class: str = "text-gray-400 bg-gray-100 cursor-not-allowed",
    query_params: Optional[dict] = None,
) -> Markup:
    """Jinja2 function to render a cross-site link as a styled button.

    Usage:
        {{ cross_link_button('risk_item', item.r_yid, 'View Risk') }}

    Args:
        entity_type: The type of entity
        entity_id: The entity's identifier
        label: Button text. If None, uses "Open in {microsite_name}".
        btn_class: Base CSS classes for the button
        active_class: Additional classes when accessible
        disabled_class: Additional classes when not accessible
        query_params: Optional query parameters

    Returns:
        Markup for a styled button/link
    """
    try:
        info = jinja_deep_link_info(entity_type, entity_id, query_params)
    except Exception as e:
        current_app.logger.warning(f"Cross link button failed: {e}")
        return Markup(
            f'<span class="{btn_class} {disabled_class}">Unavailable</span>'
        )

    btn_label = label or f"Open in {info.microsite_name}"
    icon_svg = '<svg class="ml-1.5 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>'

    if info.accessible:
        return Markup(
            f'<a href="{info.url}" class="{btn_class} {active_class}" '
            f'target="_blank" rel="noopener noreferrer">'
            f'{btn_label}{icon_svg}</a>'
        )
    else:
        return Markup(
            f'<span class="{btn_class} {disabled_class}" '
            f'title="No access to {info.microsite_name}">'
            f'{btn_label}</span>'
        )


def setup_deeplinks(
    app: Flask,
    env: Optional[str] = None,
    yaml_path: Optional[str] = None,
    microsite: Optional[Dict[str, Any]] = None,
    entities: Optional[List[Dict[str, Any]]] = None,
    # Federation options
    enable_federation: bool = False,
    auth_service_url: Optional[str] = None,
    expose_references: bool = False,
) -> None:
    """Set up deep linking for a Flask application.

    Registers Jinja2 global functions for template use and optionally
    registers entity definitions and federation.

    Usage Options:

    Option 1: Load from YAML file
        setup_deeplinks(app, yaml_path="deeplinks.yaml", env="dev")

    Option 2: Register programmatically
        setup_deeplinks(
            app,
            env="dev",
            microsite={
                "id": "risk",
                "name": "Risk Dashboard",
                "urls": {"dev": "http://localhost:5012", "uat": "...", "prd": "..."}
            },
            entities=[
                {"type": "risk_item", "path": "/items/{id}"},
            ]
        )

    Option 3: With federation (discover entities from other microsites)
        setup_deeplinks(
            app,
            env="dev",
            enable_federation=True,  # Queries auth service + microsites
            expose_references=True,  # Exposes /api/v1/references
        )

    Option 4: Just set up Jinja (entities registered elsewhere)
        setup_deeplinks(app, env="dev")

    Args:
        app: Flask application instance
        env: Environment ('dev', 'uat', 'prd'). If None, auto-detects.
        yaml_path: Path to YAML configuration file
        microsite: Microsite configuration dict (id, name, urls)
        entities: List of entity definitions (type, path, description)
        enable_federation: If True, discover entities from other microsites
        auth_service_url: URL for auth service (for federation discovery).
            If None, uses app.config['AUTH_SERVICE_URL']
        expose_references: If True, register /api/v1/references endpoint
    """
    # Set environment if specified
    if env:
        Environment.set(env)

    # Load from YAML if specified
    if yaml_path:
        from .yaml_loader import load_from_yaml
        load_from_yaml(yaml_path)

    # Register entities programmatically if specified
    if microsite and entities:
        from .registry import register_entities
        register_entities(
            microsite_id=microsite["id"],
            name=microsite.get("name"),
            urls=microsite["urls"],
            entities=entities,
        )
        # Store microsite ID for references endpoint
        app.config["DEEPLINK_MICROSITE_ID"] = microsite["id"]
    elif microsite or entities:
        app.logger.warning(
            "setup_deeplinks: Both 'microsite' and 'entities' must be provided "
            "for programmatic registration. Skipping registration."
        )

    # Store microsite ID from YAML if loaded
    if yaml_path and "DEEPLINK_MICROSITE_ID" not in app.config:
        from .registry import list_microsites
        microsites = list_microsites()
        if microsites:
            app.config["DEEPLINK_MICROSITE_ID"] = microsites[0]

    # Set up federation if enabled
    if enable_federation:
        # Get auth service URL
        federation_url = auth_service_url or app.config.get("AUTH_SERVICE_URL")

        if federation_url:
            from .federation import configure_federation, FederationConfig

            config = FederationConfig(
                auth_service_url=federation_url,
                startup_fetch=True,
                refresh_interval_seconds=app.config.get(
                    "DEEPLINK_REFRESH_INTERVAL", 300
                ),
                self_microsite_id=app.config.get("DEEPLINK_MICROSITE_ID"),
            )
            configure_federation(config)
            app.logger.info(
                f"Deep link federation enabled: auth_service={federation_url}"
            )
        else:
            app.logger.warning(
                "setup_deeplinks: enable_federation=True but no auth_service_url provided. "
                "Set auth_service_url or app.config['AUTH_SERVICE_URL']."
            )

    # Expose references endpoint if requested
    if expose_references:
        from .blueprint import references_bp

        app.register_blueprint(references_bp)
        app.logger.info("Deep link references endpoint registered: /api/v1/references")

    # Register Jinja2 globals
    app.jinja_env.globals["deep_link"] = deep_link
    app.jinja_env.globals["deep_link_info"] = jinja_deep_link_info
    app.jinja_env.globals["cross_link"] = cross_link
    app.jinja_env.globals["cross_link_button"] = cross_link_button

    # Log setup
    from .registry import list_entity_types, list_microsites

    app.logger.info(
        f"Deep links configured: env={Environment.get()}, "
        f"microsites={len(list_microsites())}, entities={len(list_entity_types())}"
    )
