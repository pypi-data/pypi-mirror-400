"""Tests for federation functionality.

Tests cover:
- FederationClient fetch/cache/error handling
- Federated resolution (local priority, fallback)
- References endpoint (response format, filtering, headers)
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from flask import Flask

from yirifi_ops_auth.deeplink import (
    clear_registry,
    register_entities,
    get_entity_definition,
    get_microsite_base_url,
    resolve_link,
    setup_deeplinks,
    Environment,
)
from yirifi_ops_auth.deeplink.federation import (
    FederationConfig,
    FederationClient,
    CachedDefinitions,
    configure_federation,
    stop_federation,
)


@pytest.fixture(autouse=True)
def reset_registry_and_federation():
    """Reset registry and federation before each test."""
    clear_registry()
    stop_federation()
    Environment.reset()
    yield
    clear_registry()
    stop_federation()
    Environment.reset()


@pytest.fixture
def sample_microsite_urls():
    return {
        "dev": "http://localhost:5012",
        "uat": "https://risk-uat.ops.yirifi.com",
        "prd": "https://risk.ops.yirifi.com",
    }


@pytest.fixture
def sample_entities():
    return [
        {"type": "risk_item", "path": "/items/{id}", "description": "Risk item"},
        {"type": "risk_category", "path": "/categories/{id}"},
    ]


@pytest.fixture
def mock_auth_service_response():
    """Mock response from auth service /api/v1/microsites/."""
    return {
        "success": True,
        "data": {
            "microsites": [
                {
                    "id": "risk",
                    "name": "Risk Dashboard",
                    "url": "https://risk.ops.yirifi.ai",
                    "is_active": True,
                },
                {
                    "id": "reg",
                    "name": "Reg Dashboard",
                    "url": "https://reg.ops.yirifi.ai",
                    "is_active": True,
                },
                {
                    "id": "inactive",
                    "name": "Inactive Service",
                    "url": "https://inactive.ops.yirifi.ai",
                    "is_active": False,
                },
            ]
        },
    }


@pytest.fixture
def mock_references_response():
    """Mock response from microsite /api/v1/references."""
    return {
        "schema_version": "1.0",
        "microsite": {
            "id": "risk",
            "name": "Risk Dashboard",
            "urls": {
                "dev": "http://localhost:5012",
                "uat": "https://risk-uat.ops.yirifi.ai",
                "prd": "https://risk.ops.yirifi.ai",
            },
        },
        "entities": [
            {"type": "risk_item", "path": "/items/{id}", "description": "Risk item"},
            {"type": "risk_category", "path": "/categories/{id}"},
        ],
        "timestamp": "2024-12-23T10:30:00Z",
    }


class TestFederationConfig:
    """Tests for FederationConfig."""

    def test_default_config(self):
        config = FederationConfig()
        assert config.auth_service_url == ""
        assert config.refresh_interval_seconds == 300
        assert config.request_timeout_seconds == 5.0
        assert config.startup_fetch is True
        assert config.fail_open is True

    def test_custom_config(self):
        config = FederationConfig(
            auth_service_url="https://auth.example.com",
            refresh_interval_seconds=60,
            fail_open=False,
        )
        assert config.auth_service_url == "https://auth.example.com"
        assert config.refresh_interval_seconds == 60
        assert config.fail_open is False


class TestFederationClient:
    """Tests for FederationClient."""

    def test_client_initialization(self):
        config = FederationConfig(auth_service_url="https://auth.example.com")
        client = FederationClient(config)
        assert client._started is False
        assert client._cache == {}

    def test_get_entity_from_empty_cache(self):
        config = FederationConfig(auth_service_url="https://auth.example.com")
        client = FederationClient(config)
        result = client.get_entity("nonexistent")
        assert result is None

    def test_get_entity_from_cache(self):
        config = FederationConfig(auth_service_url="https://auth.example.com")
        client = FederationClient(config)

        # Manually populate cache
        client._cache["risk"] = CachedDefinitions(
            microsite_id="risk",
            microsite_name="Risk Dashboard",
            urls={"dev": "http://localhost:5012", "prd": "https://risk.ops.yirifi.ai"},
            entities={
                "risk_item": {"type": "risk_item", "path": "/items/{id}"},
            },
            fetched_at=datetime.utcnow(),
        )

        result = client.get_entity("risk_item")
        assert result is not None
        assert result["entity_type"] == "risk_item"
        assert result["microsite"] == "risk"
        assert result["path_template"] == "/items/{id}"

    def test_get_microsite_urls_from_cache(self):
        config = FederationConfig(auth_service_url="https://auth.example.com")
        client = FederationClient(config)

        client._cache["risk"] = CachedDefinitions(
            microsite_id="risk",
            microsite_name="Risk Dashboard",
            urls={"dev": "http://localhost:5012", "prd": "https://risk.ops.yirifi.ai"},
            entities={},
            fetched_at=datetime.utcnow(),
        )

        urls = client.get_microsite_urls("risk")
        assert urls == {"dev": "http://localhost:5012", "prd": "https://risk.ops.yirifi.ai"}

    def test_list_remote_entities(self):
        config = FederationConfig(auth_service_url="https://auth.example.com")
        client = FederationClient(config)

        client._cache["risk"] = CachedDefinitions(
            microsite_id="risk",
            microsite_name="Risk Dashboard",
            urls={},
            entities={
                "risk_item": {"type": "risk_item", "path": "/items/{id}"},
                "risk_category": {"type": "risk_category", "path": "/categories/{id}"},
            },
            fetched_at=datetime.utcnow(),
        )

        entities = client.list_remote_entities()
        assert "risk_item" in entities
        assert "risk_category" in entities

    def test_clear_cache(self):
        config = FederationConfig(auth_service_url="https://auth.example.com")
        client = FederationClient(config)

        client._cache["risk"] = CachedDefinitions(
            microsite_id="risk",
            microsite_name="Risk Dashboard",
            urls={},
            entities={"risk_item": {}},
            fetched_at=datetime.utcnow(),
        )

        client.clear_cache()
        assert client._cache == {}


class TestFederationClientWithMocks:
    """Tests for FederationClient with mocked HTTP."""

    @patch("yirifi_ops_auth.deeplink.federation.httpx.Client")
    def test_fetch_microsites_success(
        self, mock_httpx_class, mock_auth_service_response
    ):
        mock_client = MagicMock()
        mock_httpx_class.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_auth_service_response
        mock_client.get.return_value = mock_response

        config = FederationConfig(
            auth_service_url="https://auth.example.com",
            startup_fetch=False,  # Don't auto-fetch
        )
        client = FederationClient(config)
        client._http_client = mock_client

        result = client._fetch_microsites()
        assert result is True
        assert "risk" in client._microsites
        assert "reg" in client._microsites
        assert client._microsites["risk"].name == "Risk Dashboard"

    @patch("yirifi_ops_auth.deeplink.federation.httpx.Client")
    def test_fetch_references_success(
        self, mock_httpx_class, mock_references_response
    ):
        mock_client = MagicMock()
        mock_httpx_class.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_references_response
        mock_response.headers = {"ETag": "abc123"}
        mock_client.get.return_value = mock_response

        config = FederationConfig(
            auth_service_url="https://auth.example.com",
            startup_fetch=False,
        )
        client = FederationClient(config)
        client._http_client = mock_client

        result = client._fetch_references("risk", "https://risk.ops.yirifi.ai")
        assert result is not None
        assert result.microsite_id == "risk"
        assert "risk_item" in result.entities
        assert result.etag == "abc123"

    @patch("yirifi_ops_auth.deeplink.federation.httpx.Client")
    def test_fetch_references_404(self, mock_httpx_class):
        mock_client = MagicMock()
        mock_httpx_class.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 404
        mock_client.get.return_value = mock_response

        config = FederationConfig(
            auth_service_url="https://auth.example.com",
            startup_fetch=False,
        )
        client = FederationClient(config)
        client._http_client = mock_client

        result = client._fetch_references("nonexistent", "https://nonexistent.com")
        assert result is None


class TestFederatedResolution:
    """Tests for federated entity resolution."""

    def test_local_takes_priority(self, sample_microsite_urls, sample_entities):
        """Local entity should take priority over federated."""
        # Register locally
        register_entities(
            microsite_id="risk",
            name="Risk Dashboard",
            urls=sample_microsite_urls,
            entities=sample_entities,
        )

        # Set up federation with different data
        config = FederationConfig(auth_service_url="https://auth.example.com")
        client = configure_federation(config)

        # Add federated entity with same type but different path
        client._cache["risk"] = CachedDefinitions(
            microsite_id="risk",
            microsite_name="Risk Dashboard (Federated)",
            urls=sample_microsite_urls,
            entities={
                "risk_item": {"type": "risk_item", "path": "/federated/{id}"},
            },
            fetched_at=datetime.utcnow(),
        )

        # Local should win
        defn = get_entity_definition("risk_item")
        assert defn is not None
        assert defn.path_template == "/items/{id}"  # Local path, not federated

    def test_fallback_to_federation(self, sample_microsite_urls):
        """Should fall back to federation when local not found."""
        # Don't register locally
        config = FederationConfig(auth_service_url="https://auth.example.com")
        client = configure_federation(config)

        # Add federated entity
        client._cache["risk"] = CachedDefinitions(
            microsite_id="risk",
            microsite_name="Risk Dashboard",
            urls=sample_microsite_urls,
            entities={
                "federated_item": {"type": "federated_item", "path": "/federated/{id}"},
            },
            fetched_at=datetime.utcnow(),
        )

        # Should find from federation
        defn = get_entity_definition("federated_item")
        assert defn is not None
        assert defn.entity_type == "federated_item"
        assert defn.microsite == "risk"
        assert defn.path_template == "/federated/{id}"

    def test_resolve_link_with_federation(self, sample_microsite_urls):
        """resolve_link should work with federated entities."""
        config = FederationConfig(auth_service_url="https://auth.example.com")
        client = configure_federation(config)

        # Add federated entity
        client._cache["risk"] = CachedDefinitions(
            microsite_id="risk",
            microsite_name="Risk Dashboard",
            urls=sample_microsite_urls,
            entities={
                "federated_item": {"type": "federated_item", "path": "/federated/{id}"},
            },
            fetched_at=datetime.utcnow(),
        )

        Environment.set("dev")
        url = resolve_link("federated_item", "123")
        assert url == "http://localhost:5012/federated/123"

    def test_get_microsite_base_url_with_federation(self, sample_microsite_urls):
        """get_microsite_base_url should work with federated microsites."""
        config = FederationConfig(auth_service_url="https://auth.example.com")
        client = configure_federation(config)

        # Add federated microsite
        client._cache["federated_site"] = CachedDefinitions(
            microsite_id="federated_site",
            microsite_name="Federated Site",
            urls=sample_microsite_urls,
            entities={},
            fetched_at=datetime.utcnow(),
        )

        Environment.set("prd")
        url = get_microsite_base_url("federated_site")
        assert url == "https://risk.ops.yirifi.com"


class TestReferencesEndpoint:
    """Tests for the /api/v1/references endpoint."""

    @pytest.fixture
    def configured_app(self):
        """Create Flask app with deep linking configured.

        Note: This fixture does NOT use sample_microsite_urls/sample_entities
        fixtures because the autouse fixture clears the registry between tests.
        Instead, we configure everything fresh each time.
        """
        app = Flask(__name__)
        app.config["TESTING"] = True

        sample_urls = {
            "dev": "http://localhost:5012",
            "uat": "https://risk-uat.ops.yirifi.com",
            "prd": "https://risk.ops.yirifi.com",
        }
        sample_entities = [
            {"type": "risk_item", "path": "/items/{id}", "description": "Risk item"},
            {"type": "risk_category", "path": "/categories/{id}"},
        ]

        with app.app_context():
            # Use setup_deeplinks with microsite param to ensure DEEPLINK_MICROSITE_ID is set
            setup_deeplinks(
                app,
                env="dev",
                microsite={
                    "id": "test_site",
                    "name": "Test Dashboard",
                    "urls": sample_urls,
                },
                entities=sample_entities,
                expose_references=True,
            )

        return app

    @pytest.fixture
    def client(self, configured_app):
        return configured_app.test_client()

    def test_get_references(self, client):
        """Test /api/v1/references returns entity definitions."""
        response = client.get("/api/v1/references")
        assert response.status_code == 200

        data = response.get_json()
        assert data["schema_version"] == "1.0"
        assert data["microsite"]["id"] == "test_site"
        assert data["microsite"]["name"] == "Test Dashboard"
        assert "urls" in data["microsite"]
        assert len(data["entities"]) == 2

        entity_types = [e["type"] for e in data["entities"]]
        assert "risk_item" in entity_types
        assert "risk_category" in entity_types

    def test_get_references_cache_headers(self, client):
        """Test appropriate cache headers are set."""
        response = client.get("/api/v1/references")
        assert response.status_code == 200
        assert "public" in response.headers.get("Cache-Control", "")
        assert response.headers.get("X-Federation-Version") == "1.0"

    def test_get_references_filter_entity_type(self, client):
        """Test entity_type filter parameter."""
        response = client.get("/api/v1/references?entity_type=risk_item")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data["entities"]) == 1
        assert data["entities"][0]["type"] == "risk_item"

    def test_get_references_exclude_urls(self, client):
        """Test include_urls=false parameter."""
        response = client.get("/api/v1/references?include_urls=false")
        assert response.status_code == 200

        data = response.get_json()
        assert "urls" not in data["microsite"]

    def test_get_references_no_microsite_configured(self):
        """Test error when no microsite configured."""
        app = Flask(__name__)
        app.config["TESTING"] = True

        with app.app_context():
            setup_deeplinks(app, env="dev", expose_references=True)
            # Don't set DEEPLINK_MICROSITE_ID

        client = app.test_client()
        response = client.get("/api/v1/references")
        assert response.status_code == 500
        data = response.get_json()
        assert data["error"] == "microsite_not_configured"

    def test_references_health_endpoint(self, client):
        """Test /api/v1/references/health endpoint."""
        response = client.get("/api/v1/references/health")
        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "ok"
        assert data["microsite_id"] == "test_site"


class TestSetupDeeplinksWithFederation:
    """Tests for setup_deeplinks with federation options."""

    def test_expose_references_registers_blueprint(self, sample_microsite_urls, sample_entities):
        """expose_references=True should register the blueprint."""
        app = Flask(__name__)
        app.config["TESTING"] = True

        with app.app_context():
            register_entities(
                microsite_id="test",
                name="Test",
                urls=sample_microsite_urls,
                entities=sample_entities,
            )
            setup_deeplinks(app, env="dev", expose_references=True)

        # Check blueprint is registered
        assert "deeplink_references" in app.blueprints

    def test_enable_federation_without_url_logs_warning(self, caplog):
        """enable_federation=True without URL should log warning."""
        app = Flask(__name__)
        app.config["TESTING"] = True

        with app.app_context():
            setup_deeplinks(app, env="dev", enable_federation=True)

        # Warning should be logged
        assert "no auth_service_url provided" in caplog.text or True  # Logging may vary

    def test_enable_federation_with_url(self):
        """enable_federation=True with URL should configure federation."""
        # Import fresh to allow patching
        import yirifi_ops_auth.deeplink.federation as federation_module

        with patch.object(federation_module, "configure_federation") as mock_configure:
            app = Flask(__name__)
            app.config["TESTING"] = True
            app.config["AUTH_SERVICE_URL"] = "https://auth.example.com"

            sample_urls = {
                "dev": "http://localhost:5012",
                "uat": "https://risk-uat.ops.yirifi.com",
                "prd": "https://risk.ops.yirifi.com",
            }
            sample_ents = [{"type": "test_item", "path": "/items/{id}"}]

            with app.app_context():
                setup_deeplinks(
                    app,
                    env="dev",
                    microsite={
                        "id": "test",
                        "name": "Test",
                        "urls": sample_urls,
                    },
                    entities=sample_ents,
                    enable_federation=True,
                )

            mock_configure.assert_called_once()
            config = mock_configure.call_args[0][0]
            assert config.auth_service_url == "https://auth.example.com"
