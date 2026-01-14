"""Tests for the deep linking module."""

import pytest
from dataclasses import dataclass
from typing import List

from yirifi_ops_auth.deeplink import (
    # Registration
    register_entities,
    register_microsite,
    register_entity,
    clear_registry,
    # Core resolution
    resolve_link,
    deep_link_info,
    can_link_to,
    DeepLinkInfo,
    UnknownEntityTypeError,
    RegistrationError,
    # Registry queries
    get_entity_definition,
    get_microsite_for_entity,
    get_microsite_config,
    get_microsite_base_url,
    list_entity_types,
    list_entity_types_for_microsite,
    list_microsites,
    # Environment
    Environment,
    get_environment,
    set_environment,
)


# ============================================
# Test Fixtures
# ============================================

@dataclass
class MockUser:
    """Mock user for testing access control."""
    microsites: List[str]

    def has_access_to(self, microsite: str) -> bool:
        return microsite in self.microsites


@pytest.fixture(autouse=True)
def reset_registry_and_env():
    """Clear registry and reset environment before each test."""
    clear_registry()
    Environment.reset()
    yield
    clear_registry()
    Environment.reset()


@pytest.fixture
def sample_microsites():
    """Register sample microsites for testing."""
    register_microsite(
        id="risk",
        name="Risk Dashboard",
        urls={
            "dev": "http://localhost:5012",
            "uat": "https://risk-uat.ops.yirifi.com",
            "prd": "https://risk.ops.yirifi.com",
        }
    )
    register_microsite(
        id="ums",
        name="User Management",
        urls={
            "dev": "http://localhost:5013",
            "uat": "https://ums-uat.ops.yirifi.com",
            "prd": "https://ums.ops.yirifi.com",
        }
    )
    register_microsite(
        id="reg",
        name="Reg Dashboard",
        urls={
            "dev": "http://localhost:5000",
            "uat": "https://reg-uat.ops.yirifi.com",
            "prd": "https://reg.ops.yirifi.com",
        }
    )


@pytest.fixture
def sample_entities(sample_microsites):
    """Register sample entities for testing."""
    register_entity(
        entity_type="risk_item",
        microsite="risk",
        path_template="/risk-management/collections/risk_items/{id}",
        description="Risk management item",
    )
    register_entity(
        entity_type="risk_hierarchy",
        microsite="risk",
        path_template="/risk-management/collections/risk_hierarchies/{id}",
    )
    register_entity(
        entity_type="user",
        microsite="ums",
        path_template="/users/{id}",
        description="User profile",
    )
    register_entity(
        entity_type="reg_link",
        microsite="reg",
        path_template="/regulatory-status/links/{id}",
    )


@pytest.fixture
def user_with_risk_access():
    return MockUser(microsites=['risk', 'reg'])


@pytest.fixture
def user_without_risk_access():
    return MockUser(microsites=['reg'])


# ============================================
# Registration Tests
# ============================================

class TestRegistration:
    def test_register_microsite(self):
        register_microsite(
            id="test",
            name="Test Dashboard",
            urls={
                "dev": "http://localhost:9999",
                "uat": "https://test-uat.example.com",
                "prd": "https://test.example.com",
            }
        )
        assert "test" in list_microsites()
        config = get_microsite_config("test")
        assert config.name == "Test Dashboard"
        assert config.dev_url == "http://localhost:9999"

    def test_register_microsite_missing_url(self):
        with pytest.raises(RegistrationError) as exc_info:
            register_microsite(
                id="test",
                name="Test",
                urls={"dev": "http://localhost:9999"}  # Missing uat and prd
            )
        assert "missing URLs" in str(exc_info.value)

    def test_register_entity(self, sample_microsites):
        register_entity(
            entity_type="test_item",
            microsite="risk",
            path_template="/items/{id}",
            description="Test item",
        )
        defn = get_entity_definition("test_item")
        assert defn is not None
        assert defn.microsite == "risk"
        assert defn.path_template == "/items/{id}"

    def test_register_entity_without_microsite(self):
        with pytest.raises(RegistrationError) as exc_info:
            register_entity(
                entity_type="orphan",
                microsite="nonexistent",
                path_template="/orphan/{id}",
            )
        assert "not registered" in str(exc_info.value)

    def test_register_entity_invalid_path(self, sample_microsites):
        with pytest.raises(RegistrationError) as exc_info:
            register_entity(
                entity_type="bad",
                microsite="risk",
                path_template="/no-id-placeholder",
            )
        assert "{id}" in str(exc_info.value)

    def test_register_entities_bulk(self):
        register_entities(
            microsite_id="bulk",
            name="Bulk Dashboard",
            urls={
                "dev": "http://localhost:8000",
                "uat": "https://bulk-uat.example.com",
                "prd": "https://bulk.example.com",
            },
            entities=[
                {"type": "item_a", "path": "/a/{id}"},
                {"type": "item_b", "path": "/b/{id}", "description": "Item B"},
            ]
        )
        assert "bulk" in list_microsites()
        assert "item_a" in list_entity_types()
        assert "item_b" in list_entity_types()

    def test_clear_registry(self, sample_entities):
        assert len(list_entity_types()) > 0
        assert len(list_microsites()) > 0
        clear_registry()
        assert len(list_entity_types()) == 0
        assert len(list_microsites()) == 0


# ============================================
# Registry Query Tests
# ============================================

class TestRegistry:
    def test_get_entity_definition_exists(self, sample_entities):
        defn = get_entity_definition('risk_item')
        assert defn is not None
        assert defn.microsite == 'risk'
        assert '{id}' in defn.path_template

    def test_get_entity_definition_not_exists(self, sample_entities):
        defn = get_entity_definition('nonexistent_entity')
        assert defn is None

    def test_get_microsite_for_entity(self, sample_entities):
        assert get_microsite_for_entity('risk_item') == 'risk'
        assert get_microsite_for_entity('user') == 'ums'
        assert get_microsite_for_entity('nonexistent') is None

    def test_list_entity_types(self, sample_entities):
        types = list_entity_types()
        assert 'risk_item' in types
        assert 'user' in types
        assert 'reg_link' in types
        assert len(types) == 4

    def test_list_entity_types_for_microsite(self, sample_entities):
        risk_types = list_entity_types_for_microsite('risk')
        assert 'risk_item' in risk_types
        assert 'risk_hierarchy' in risk_types
        assert 'user' not in risk_types

        ums_types = list_entity_types_for_microsite('ums')
        assert 'user' in ums_types


# ============================================
# Environment Tests
# ============================================

class TestEnvironment:
    def test_get_environment_default(self):
        assert get_environment() == 'dev'

    def test_set_environment(self):
        set_environment('prd')
        assert get_environment() == 'prd'

        set_environment('uat')
        assert get_environment() == 'uat'

    def test_set_environment_invalid(self):
        with pytest.raises(ValueError):
            set_environment('invalid')

    def test_environment_override_context_manager(self):
        set_environment('dev')
        assert Environment.get() == 'dev'

        with Environment.override('prd'):
            assert Environment.get() == 'prd'

        assert Environment.get() == 'dev'  # Restored

    def test_environment_normalization(self):
        Environment.set('development')
        assert Environment.get() == 'dev'

        Environment.set('production')
        assert Environment.get() == 'prd'

        Environment.set('staging')
        assert Environment.get() == 'uat'

    def test_get_microsite_base_url_dev(self, sample_microsites):
        set_environment('dev')
        url = get_microsite_base_url('risk')
        assert url is not None
        assert 'localhost' in url

    def test_get_microsite_base_url_prd(self, sample_microsites):
        set_environment('prd')
        url = get_microsite_base_url('risk')
        assert url is not None
        assert 'localhost' not in url
        assert 'yirifi.com' in url

    def test_get_microsite_base_url_unknown(self, sample_microsites):
        url = get_microsite_base_url('nonexistent')
        assert url is None

    def test_list_microsites(self, sample_microsites):
        sites = list_microsites()
        assert 'risk' in sites
        assert 'reg' in sites
        assert len(sites) == 3


# ============================================
# Resolver Tests
# ============================================

class TestResolver:
    def test_resolve_link_basic(self, sample_entities):
        set_environment('dev')
        url = resolve_link('risk_item', 'r_yid_123')
        assert 'localhost' in url
        assert 'r_yid_123' in url
        assert '/risk-management/' in url

    def test_resolve_link_with_numeric_id(self, sample_entities):
        url = resolve_link('user', 42)
        assert '/users/42' in url

    def test_resolve_link_with_query_params(self, sample_entities):
        url = resolve_link('user', 123, query_params={'tab': 'permissions'})
        assert '?tab=permissions' in url

    def test_resolve_link_different_environments(self, sample_entities):
        set_environment('dev')
        dev_url = resolve_link('risk_item', 'test')
        assert 'localhost' in dev_url

        set_environment('prd')
        prd_url = resolve_link('risk_item', 'test')
        assert 'localhost' not in prd_url

    def test_resolve_link_unknown_entity(self, sample_entities):
        with pytest.raises(UnknownEntityTypeError):
            resolve_link('nonexistent_type', 'id')

    def test_resolve_link_url_encodes_id(self, sample_entities):
        url = resolve_link('user', 'user/with/slashes')
        assert 'user%2Fwith%2Fslashes' in url


class TestDeepLinkInfo:
    def test_deep_link_info_accessible(self, sample_entities, user_with_risk_access):
        info = deep_link_info('risk_item', 'r_yid_123', user=user_with_risk_access)
        assert isinstance(info, DeepLinkInfo)
        assert info.accessible is True
        assert info.microsite == 'risk'
        assert 'Risk' in info.microsite_name
        assert 'r_yid_123' in info.url

    def test_deep_link_info_not_accessible(self, sample_entities, user_without_risk_access):
        info = deep_link_info('risk_item', 'r_yid_123', user=user_without_risk_access)
        assert info.accessible is False
        assert info.url is not None  # URL still generated

    def test_deep_link_info_no_user(self, sample_entities):
        info = deep_link_info('risk_item', 'r_yid_123', user=None)
        assert info.accessible is True  # Default to accessible when no user

    def test_deep_link_info_entity_type_returned(self, sample_entities):
        info = deep_link_info('user', 42)
        assert info.entity_type == 'user'
        assert info.entity_id == '42'


class TestCanLinkTo:
    def test_can_link_to_with_access(self, sample_entities, user_with_risk_access):
        assert can_link_to('risk_item', user_with_risk_access) is True

    def test_can_link_to_without_access(self, sample_entities, user_without_risk_access):
        assert can_link_to('risk_item', user_without_risk_access) is False

    def test_can_link_to_no_user(self, sample_entities):
        assert can_link_to('risk_item', None) is True

    def test_can_link_to_unknown_entity(self, sample_entities):
        assert can_link_to('nonexistent', None) is False


# ============================================
# Integration Tests
# ============================================

class TestIntegration:
    def test_full_flow_accessible(self, sample_entities, user_with_risk_access):
        """Test the full flow for an accessible link."""
        # 1. Check entity exists
        assert get_entity_definition('risk_item') is not None

        # 2. Check user can access
        assert can_link_to('risk_item', user_with_risk_access) is True

        # 3. Get link info
        info = deep_link_info('risk_item', 'test123', user=user_with_risk_access)
        assert info.accessible is True
        assert info.microsite == 'risk'

        # 4. Resolve URL
        url = resolve_link('risk_item', 'test123')
        assert url == info.url

    def test_full_flow_not_accessible(self, sample_entities, user_without_risk_access):
        """Test the full flow for a non-accessible link."""
        # 1. Check entity exists
        assert get_entity_definition('risk_item') is not None

        # 2. Check user cannot access
        assert can_link_to('risk_item', user_without_risk_access) is False

        # 3. Get link info - should still work but accessible=False
        info = deep_link_info('risk_item', 'test123', user=user_without_risk_access)
        assert info.accessible is False
        assert info.url is not None  # URL still generated for sharing/bookmarking

    def test_all_registered_entities_have_valid_microsites(self, sample_entities):
        """Verify all registered entities reference valid microsites."""
        for entity_type in list_entity_types():
            defn = get_entity_definition(entity_type)
            url = get_microsite_base_url(defn.microsite, 'dev')
            assert url is not None, f"Entity {entity_type} references unknown microsite {defn.microsite}"

    def test_all_entity_paths_have_id_placeholder(self, sample_entities):
        """Verify all entity path templates have {id} placeholder."""
        for entity_type in list_entity_types():
            defn = get_entity_definition(entity_type)
            assert '{id}' in defn.path_template, \
                f"Entity {entity_type} path missing {{id}} placeholder"


# ============================================
# YAML Loading Tests
# ============================================

class TestYamlLoading:
    def test_load_from_string(self):
        from yirifi_ops_auth.deeplink import load_from_string

        yaml_content = """
schema_version: "1.0"
microsite:
  id: yaml_test
  name: YAML Test Dashboard
  urls:
    dev: http://localhost:7777
    uat: https://yaml-uat.example.com
    prd: https://yaml.example.com

entities:
  yaml_item:
    path: /yaml/items/{id}
    description: YAML loaded item
"""
        load_from_string(yaml_content)

        assert "yaml_test" in list_microsites()
        assert "yaml_item" in list_entity_types()

        defn = get_entity_definition("yaml_item")
        assert defn.microsite == "yaml_test"
        assert "/yaml/items/{id}" in defn.path_template

    def test_load_from_string_invalid_yaml(self):
        from yirifi_ops_auth.deeplink import load_from_string, YamlLoadError

        with pytest.raises(YamlLoadError):
            load_from_string("invalid: yaml: content: [")

    def test_load_from_string_missing_microsite(self):
        from yirifi_ops_auth.deeplink import load_from_string, YamlLoadError

        yaml_content = """
schema_version: "1.0"
entities:
  orphan:
    path: /orphan/{id}
"""
        with pytest.raises(YamlLoadError) as exc_info:
            load_from_string(yaml_content)
        assert "microsite" in str(exc_info.value).lower()

    def test_load_from_string_missing_path(self):
        from yirifi_ops_auth.deeplink import load_from_string, YamlLoadError

        yaml_content = """
schema_version: "1.0"
microsite:
  id: test
  name: Test
  urls:
    dev: http://localhost:1234
    uat: https://test-uat.example.com
    prd: https://test.example.com

entities:
  bad_entity:
    description: No path defined
"""
        with pytest.raises(YamlLoadError) as exc_info:
            load_from_string(yaml_content)
        assert "path" in str(exc_info.value).lower()
