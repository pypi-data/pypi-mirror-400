"""Flask blueprint for exposing entity references via API.

This blueprint exposes the /api/v1/references endpoint that returns
this microsite's entity definitions for federation discovery.

Usage:
    from yirifi_ops_auth.deeplink import setup_deeplinks

    # In your app factory
    setup_deeplinks(
        app,
        expose_references=True,  # Registers this blueprint
    )

    # Or manually:
    from yirifi_ops_auth.deeplink.blueprint import references_bp
    app.register_blueprint(references_bp)
"""

from datetime import datetime
from flask import Blueprint, jsonify, request, current_app

from .registry import (
    get_microsite_config,
    list_entity_types_for_microsite,
    get_entity_definition,
)


references_bp = Blueprint("deeplink_references", __name__, url_prefix="/api/v1")


@references_bp.route("/references", methods=["GET"])
def get_references():
    """Expose this microsite's entity definitions for federation.

    This endpoint allows other microsites to discover what entity types
    this microsite serves and how to construct URLs for them.

    Query Parameters:
        entity_type (str, optional): Filter to specific entity type
        include_urls (bool, default=true): Include URL mappings in response

    Returns:
        JSON response with schema:
        {
            "schema_version": "1.0",
            "microsite": {
                "id": "risk",
                "name": "Risk Dashboard",
                "urls": {
                    "dev": "http://localhost:5012",
                    "uat": "https://risk-uat.ops.yirifi.com",
                    "prd": "https://risk.ops.yirifi.com"
                }
            },
            "entities": [
                {
                    "type": "risk_item",
                    "path": "/items/{id}",
                    "description": "Risk management item"
                }
            ],
            "timestamp": "2024-12-23T10:30:00Z"
        }

    Response Headers:
        Cache-Control: public, max-age=300
        X-Federation-Version: 1.0
    """
    # Get microsite config (set during setup)
    microsite_id = current_app.config.get("DEEPLINK_MICROSITE_ID")
    if not microsite_id:
        return (
            jsonify(
                {
                    "error": "microsite_not_configured",
                    "message": "This microsite has not configured deep linking. "
                    "Call setup_deeplinks() with a microsite parameter.",
                }
            ),
            500,
        )

    config = get_microsite_config(microsite_id)
    if not config:
        return (
            jsonify(
                {
                    "error": "microsite_not_found",
                    "message": f"Microsite '{microsite_id}' not registered in local registry.",
                }
            ),
            500,
        )

    # Parse query parameters
    entity_type_filter = request.args.get("entity_type")
    include_urls = request.args.get("include_urls", "true").lower() == "true"

    # Get entities for this microsite
    entity_types = list_entity_types_for_microsite(microsite_id)

    if entity_type_filter:
        entity_types = [et for et in entity_types if et == entity_type_filter]

    entities = []
    for entity_type in entity_types:
        defn = get_entity_definition(entity_type)
        if defn:
            entity_data = {
                "type": defn.entity_type,
                "path": defn.path_template,
            }
            if defn.description:
                entity_data["description"] = defn.description
            entities.append(entity_data)

    # Build response
    response_data = {
        "schema_version": "1.0",
        "microsite": {
            "id": config.id,
            "name": config.name,
        },
        "entities": entities,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if include_urls:
        response_data["microsite"]["urls"] = config.urls

    # Build response with cache headers
    resp = jsonify(response_data)
    resp.headers["Cache-Control"] = "public, max-age=300"
    resp.headers["X-Federation-Version"] = "1.0"

    return resp


@references_bp.route("/references/health", methods=["GET"])
def references_health():
    """Health check for the references endpoint.

    Returns simple status for monitoring/load balancer health checks.
    """
    microsite_id = current_app.config.get("DEEPLINK_MICROSITE_ID")

    return jsonify(
        {
            "status": "ok",
            "microsite_id": microsite_id,
            "federation_version": "1.0",
        }
    )
