"""YAML configuration loader for deep linking.

Allows microsites to define their entity configurations in YAML files
instead of programmatic registration.

Example YAML file (deeplinks.yaml):

    schema_version: "1.0"
    microsite:
      id: risk
      name: Risk Dashboard
      urls:
        dev: http://localhost:5012
        uat: https://risk-uat.ops.yirifi.com
        prd: https://risk.ops.yirifi.com

    entities:
      risk_item:
        path: /risk-management/collections/risk_items/{id}
        description: Risk management item
      risk_hierarchy:
        path: /risk-management/collections/risk_hierarchies/{id}

Usage:
    from yirifi_ops_auth.deeplink import load_from_yaml

    # Load from file path
    load_from_yaml("deeplinks.yaml")

    # Or with Path object
    from pathlib import Path
    load_from_yaml(Path("config/deeplinks.yaml"))
"""

import logging
from pathlib import Path
from typing import Union, Optional

logger = logging.getLogger(__name__)

# Supported schema versions
SUPPORTED_SCHEMA_VERSIONS = {"1.0"}


class YamlLoadError(Exception):
    """Raised when YAML loading or validation fails."""
    pass


def load_from_yaml(path: Union[str, Path]) -> None:
    """Load entity definitions from a YAML file.

    Args:
        path: Path to the YAML configuration file

    Raises:
        YamlLoadError: If file not found, YAML invalid, or schema validation fails
        ImportError: If PyYAML is not installed
    """
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required for YAML loading. Install with: pip install pyyaml"
        )

    path = Path(path)

    if not path.exists():
        raise YamlLoadError(f"Configuration file not found: {path}")

    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise YamlLoadError(f"Invalid YAML in {path}: {e}")

    if not data:
        raise YamlLoadError(f"Empty configuration file: {path}")

    _validate_and_register(data, source=str(path))
    logger.info(f"Loaded deep link configuration from {path}")


def load_from_string(yaml_content: str, source: str = "<string>") -> None:
    """Load entity definitions from a YAML string.

    Useful for testing or when YAML is embedded/generated.

    Args:
        yaml_content: YAML content as a string
        source: Description of source for error messages
    """
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required for YAML loading. Install with: pip install pyyaml"
        )

    try:
        data = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        raise YamlLoadError(f"Invalid YAML from {source}: {e}")

    if not data:
        raise YamlLoadError(f"Empty configuration from {source}")

    _validate_and_register(data, source=source)


def _validate_and_register(data: dict, source: str) -> None:
    """Validate YAML data and register with the registry.

    Args:
        data: Parsed YAML data
        source: Source description for error messages
    """
    from .registry import register_entities

    # Check schema version
    schema_version = data.get("schema_version", "1.0")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise YamlLoadError(
            f"Unsupported schema_version '{schema_version}' in {source}. "
            f"Supported: {SUPPORTED_SCHEMA_VERSIONS}"
        )

    # Validate microsite section
    microsite = data.get("microsite")
    if not microsite:
        raise YamlLoadError(f"Missing 'microsite' section in {source}")

    microsite_id = microsite.get("id")
    if not microsite_id:
        raise YamlLoadError(f"Missing 'microsite.id' in {source}")

    microsite_name = microsite.get("name")
    if not microsite_name:
        raise YamlLoadError(f"Missing 'microsite.name' in {source}")

    urls = microsite.get("urls")
    if not urls:
        raise YamlLoadError(f"Missing 'microsite.urls' in {source}")

    # Validate required URLs
    required_envs = {"dev", "uat", "prd"}
    missing_envs = required_envs - set(urls.keys())
    if missing_envs:
        raise YamlLoadError(
            f"Missing URLs for environments {missing_envs} in {source}"
        )

    # Validate entities section
    entities_data = data.get("entities", {})
    if not entities_data:
        logger.warning(f"No entities defined in {source}")

    # Convert to list format expected by register_entities
    entities = []
    for entity_type, entity_config in entities_data.items():
        if not isinstance(entity_config, dict):
            raise YamlLoadError(
                f"Entity '{entity_type}' must be a dict in {source}"
            )

        path = entity_config.get("path")
        if not path:
            raise YamlLoadError(
                f"Entity '{entity_type}' missing 'path' in {source}"
            )

        if "{id}" not in path:
            raise YamlLoadError(
                f"Entity '{entity_type}' path must contain {{id}}: {path}"
            )

        entities.append({
            "type": entity_type,
            "path": path,
            "description": entity_config.get("description"),
        })

    # Register everything
    register_entities(
        microsite_id=microsite_id,
        name=microsite_name,
        urls=urls,
        entities=entities,
    )

    logger.debug(
        f"Registered {len(entities)} entities for '{microsite_id}' from {source}"
    )


def discover_and_load(
    search_paths: Optional[list[Union[str, Path]]] = None,
    filenames: Optional[list[str]] = None,
) -> int:
    """Discover and load YAML files from multiple locations.

    Searches for configuration files in the given paths and loads them.

    Args:
        search_paths: Directories to search (default: current directory)
        filenames: Filenames to look for (default: deeplinks.yaml, deeplinks.yml)

    Returns:
        Number of files loaded

    Example:
        # Load from current directory
        discover_and_load()

        # Load from specific directories
        discover_and_load(search_paths=["config/", "deeplink_configs/"])
    """
    if search_paths is None:
        search_paths = [Path.cwd()]

    if filenames is None:
        filenames = ["deeplinks.yaml", "deeplinks.yml"]

    loaded_count = 0

    for search_path in search_paths:
        search_path = Path(search_path)
        if not search_path.exists():
            logger.debug(f"Search path does not exist: {search_path}")
            continue

        for filename in filenames:
            filepath = search_path / filename
            if filepath.exists():
                try:
                    load_from_yaml(filepath)
                    loaded_count += 1
                except YamlLoadError as e:
                    logger.error(f"Failed to load {filepath}: {e}")

    return loaded_count
