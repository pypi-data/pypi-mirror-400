"""Federation client for discovering entity definitions from remote microsites.

Enables cross-microsite deep linking by:
1. Querying auth service for list of microsites and their URLs
2. Querying each microsite's /api/v1/references for entity definitions
3. Caching results for fast lookup

Usage:
    from yirifi_ops_auth.deeplink import configure_federation, FederationConfig

    # Configure at app startup
    configure_federation(FederationConfig(
        auth_service_url="https://auth.ops.yirifi.ai",
    ))

    # Entity lookup automatically checks federation cache
    resolve_link('risk_item', 'r_yid_123')  # Works even if not locally registered
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import threading
import os

import httpx

from .environment import Environment

logger = logging.getLogger(__name__)


class FederationError(Exception):
    """Base exception for federation errors."""
    pass


class FederationTimeoutError(FederationError):
    """Remote microsite did not respond in time."""
    pass


class FederationConnectionError(FederationError):
    """Could not connect to remote microsite."""
    pass


@dataclass
class FederationConfig:
    """Configuration for federation behavior."""

    # Auth service URL (required for discovery)
    auth_service_url: str = ""

    # Timing
    refresh_interval_seconds: int = 300  # 5 minutes
    request_timeout_seconds: float = 5.0
    startup_fetch: bool = True

    # Caching
    cache_ttl_seconds: int = 300

    # Error handling
    max_retries: int = 2
    retry_delay_seconds: float = 1.0
    fail_open: bool = True  # Continue if remote unavailable

    # Skip self (don't query your own microsite)
    self_microsite_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.auth_service_url:
            # Try to get from environment
            self.auth_service_url = os.getenv("AUTH_SERVICE_URL", "")


@dataclass
class CachedMicrosite:
    """Cached microsite information from auth service."""
    id: str
    name: str
    url: Optional[str]  # Production URL
    is_active: bool


@dataclass
class CachedDefinitions:
    """Cached entity definitions from a microsite."""
    microsite_id: str
    microsite_name: str
    urls: Dict[str, str]  # {"dev": "...", "uat": "...", "prd": "..."}
    entities: Dict[str, Dict[str, Any]]  # entity_type -> {path, description}
    fetched_at: datetime
    etag: Optional[str] = None

    def is_stale(self, ttl_seconds: int) -> bool:
        return datetime.utcnow() - self.fetched_at > timedelta(seconds=ttl_seconds)


class FederationClient:
    """Client for fetching entity definitions from remote microsites.

    Thread-safe client that:
    1. Discovers microsites from auth service
    2. Fetches entity definitions from each microsite's /api/v1/references
    3. Caches results with configurable TTL
    4. Supports background refresh
    """

    def __init__(self, config: FederationConfig):
        self.config = config
        self._microsites: Dict[str, CachedMicrosite] = {}
        self._cache: Dict[str, CachedDefinitions] = {}
        self._lock = threading.RLock()
        self._http_client: Optional[httpx.Client] = None
        self._refresh_thread: Optional[threading.Thread] = None
        self._running = False
        self._started = False

    def start(self) -> None:
        """Start the federation client with initial fetch and background refresh."""
        if self._started:
            return

        self._http_client = httpx.Client(
            timeout=self.config.request_timeout_seconds,
            follow_redirects=True,
        )

        self._started = True
        self._running = True

        if self.config.startup_fetch:
            self._fetch_all()

        if self.config.refresh_interval_seconds > 0:
            self._start_background_refresh()

    def stop(self) -> None:
        """Stop the federation client and cleanup resources."""
        self._running = False
        self._started = False

        if self._http_client:
            self._http_client.close()
            self._http_client = None

    def get_entity(self, entity_type: str) -> Optional[Dict[str, Any]]:
        """Get entity definition from federated sources.

        Returns dict with: entity_type, microsite, microsite_name, urls, path_template, description
        """
        with self._lock:
            for microsite_id, cached in self._cache.items():
                if entity_type in cached.entities:
                    entity = cached.entities[entity_type]
                    return {
                        "entity_type": entity_type,
                        "microsite": microsite_id,
                        "microsite_name": cached.microsite_name,
                        "urls": cached.urls,
                        "path_template": entity["path"],
                        "description": entity.get("description"),
                    }
        return None

    def get_microsite_urls(self, microsite_id: str) -> Optional[Dict[str, str]]:
        """Get URLs for a microsite from federation cache."""
        with self._lock:
            cached = self._cache.get(microsite_id)
            if cached:
                return cached.urls
        return None

    def list_remote_entities(self) -> List[str]:
        """List all entity types available from federated sources."""
        with self._lock:
            entities = []
            for cached in self._cache.values():
                entities.extend(cached.entities.keys())
            return entities

    def list_remote_microsites(self) -> List[str]:
        """List all microsite IDs in federation cache."""
        with self._lock:
            return list(self._cache.keys())

    def _fetch_all(self) -> None:
        """Fetch from auth service, then all microsites."""
        # 1. Get microsite list from auth service
        if not self._fetch_microsites():
            logger.warning("Federation: failed to fetch microsites from auth service")
            return

        # 2. Fetch references from each active microsite
        current_env = Environment.get()

        with self._lock:
            microsites_to_query = [
                m for m in self._microsites.values()
                if m.is_active and m.url and m.id != self.config.self_microsite_id
            ]

        for microsite in microsites_to_query:
            try:
                self._fetch_references(microsite.id, microsite.url)
            except Exception as e:
                logger.warning(f"Federation: failed to fetch from {microsite.id}: {e}")

    def _fetch_microsites(self) -> bool:
        """Fetch microsite list from auth service."""
        if not self.config.auth_service_url:
            logger.warning("Federation: auth_service_url not configured")
            return False

        url = f"{self.config.auth_service_url.rstrip('/')}/api/v1/microsites/"

        try:
            response = self._http_client.get(url)

            if response.status_code != 200:
                logger.warning(
                    f"Federation: auth service returned {response.status_code}"
                )
                return False

            data = response.json()

            if not data.get("success"):
                logger.warning("Federation: auth service returned success=false")
                return False

            microsites_data = data.get("data", {}).get("microsites", [])

            with self._lock:
                self._microsites.clear()
                for ms in microsites_data:
                    self._microsites[ms["id"]] = CachedMicrosite(
                        id=ms["id"],
                        name=ms["name"],
                        url=ms.get("url"),
                        is_active=ms.get("is_active", True),
                    )

            logger.info(
                f"Federation: discovered {len(self._microsites)} microsites from auth service"
            )
            return True

        except httpx.TimeoutException as e:
            logger.warning(f"Federation: auth service timeout: {e}")
            if not self.config.fail_open:
                raise FederationTimeoutError(str(e))
            return False
        except httpx.RequestError as e:
            logger.warning(f"Federation: auth service connection error: {e}")
            if not self.config.fail_open:
                raise FederationConnectionError(str(e))
            return False
        except Exception as e:
            logger.error(f"Federation: error fetching microsites: {e}")
            return False

    def _fetch_references(
        self, microsite_id: str, base_url: str
    ) -> Optional[CachedDefinitions]:
        """Fetch entity definitions from a single microsite."""
        url = f"{base_url.rstrip('/')}/api/v1/references"
        headers = {}

        # Conditional request if we have cached data
        with self._lock:
            cached = self._cache.get(microsite_id)
            if cached and cached.etag:
                headers["If-None-Match"] = cached.etag

        try:
            response = self._http_client.get(url, headers=headers)

            if response.status_code == 304:
                # Not modified, update timestamp
                logger.debug(f"Federation: {microsite_id} not modified")
                with self._lock:
                    if cached:
                        cached.fetched_at = datetime.utcnow()
                return cached

            if response.status_code == 404:
                # Microsite doesn't expose references endpoint yet
                logger.debug(f"Federation: {microsite_id} has no /api/v1/references")
                return None

            if response.status_code != 200:
                logger.warning(
                    f"Federation: {microsite_id} returned {response.status_code}"
                )
                return None

            data = response.json()

            # Validate response structure
            if "microsite" not in data or "entities" not in data:
                logger.warning(f"Federation: {microsite_id} invalid response structure")
                return None

            # Parse response
            microsite_data = data["microsite"]
            definitions = CachedDefinitions(
                microsite_id=microsite_data.get("id", microsite_id),
                microsite_name=microsite_data.get("name", microsite_id.title()),
                urls=microsite_data.get("urls", {}),
                entities={e["type"]: e for e in data["entities"]},
                fetched_at=datetime.utcnow(),
                etag=response.headers.get("ETag"),
            )

            with self._lock:
                self._cache[microsite_id] = definitions

            logger.info(
                f"Federation: fetched {len(data['entities'])} entities from {microsite_id}"
            )
            return definitions

        except httpx.TimeoutException as e:
            logger.warning(f"Federation: {microsite_id} timeout: {e}")
            if not self.config.fail_open:
                raise FederationTimeoutError(str(e))
            return None
        except httpx.RequestError as e:
            logger.warning(f"Federation: failed to reach {microsite_id}: {e}")
            if not self.config.fail_open:
                raise FederationConnectionError(str(e))
            return None
        except Exception as e:
            logger.error(f"Federation: error processing {microsite_id}: {e}")
            return None

    def _start_background_refresh(self) -> None:
        """Start background thread for periodic refresh."""
        self._refresh_thread = threading.Thread(
            target=self._refresh_loop,
            daemon=True,
            name="deeplink-federation-refresh",
        )
        self._refresh_thread.start()

    def _refresh_loop(self) -> None:
        """Background refresh loop."""
        import time

        while self._running:
            time.sleep(self.config.refresh_interval_seconds)
            if self._running:
                try:
                    self._fetch_all()
                except Exception as e:
                    logger.error(f"Federation: background refresh error: {e}")

    def clear_cache(self) -> None:
        """Clear all cached data. Useful for testing."""
        with self._lock:
            self._microsites.clear()
            self._cache.clear()


# Module-level singleton
_federation_client: Optional[FederationClient] = None


def get_federation_client() -> Optional[FederationClient]:
    """Get the federation client singleton."""
    return _federation_client


def configure_federation(config: FederationConfig) -> FederationClient:
    """Configure and start the federation client.

    Args:
        config: FederationConfig with auth_service_url and other settings

    Returns:
        The configured FederationClient instance
    """
    global _federation_client

    if _federation_client:
        _federation_client.stop()

    _federation_client = FederationClient(config)
    _federation_client.start()

    return _federation_client


def stop_federation() -> None:
    """Stop the federation client."""
    global _federation_client

    if _federation_client:
        _federation_client.stop()
        _federation_client = None


def clear_federation_cache() -> None:
    """Clear federation cache. Useful for testing."""
    if _federation_client:
        _federation_client.clear_cache()
