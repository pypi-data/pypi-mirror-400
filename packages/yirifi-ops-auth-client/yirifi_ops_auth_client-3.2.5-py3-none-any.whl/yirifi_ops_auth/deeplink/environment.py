"""Thread-safe environment configuration using contextvars.

Provides isolation for environment settings across threads and async contexts,
with a context manager for temporary overrides.
"""

import os
from contextvars import ContextVar
from contextlib import contextmanager
from typing import Optional, Generator


# Thread-safe environment storage
_env_var: ContextVar[Optional[str]] = ContextVar('deeplink_env', default=None)

# Valid environments
VALID_ENVIRONMENTS = ("dev", "uat", "prd")

# Environment name aliases
ENV_ALIASES = {
    "development": "dev",
    "local": "dev",
    "staging": "uat",
    "test": "uat",
    "production": "prd",
    "prod": "prd",
}


class Environment:
    """Thread-safe environment configuration.

    Usage:
        # Get current environment
        env = Environment.get()  # -> 'dev', 'uat', or 'prd'

        # Set environment
        Environment.set('prd')

        # Temporary override (for testing)
        with Environment.override('uat'):
            # Inside this block, env is 'uat'
            do_something()
        # Outside, env is restored to previous value
    """

    VALID = VALID_ENVIRONMENTS

    @classmethod
    def get(cls) -> str:
        """Get the current environment.

        Resolution order:
        1. Explicitly set via Environment.set() (thread-local)
        2. YIRIFI_ENV environment variable
        3. FLASK_ENV environment variable
        4. Default to 'dev'

        Returns:
            Environment string: 'dev', 'uat', or 'prd'
        """
        # Check thread-local context first
        env = _env_var.get()
        if env is not None:
            return env

        # Fall back to environment variables
        return cls._from_env_vars()

    @classmethod
    def _from_env_vars(cls) -> str:
        """Read environment from OS environment variables."""
        env = os.getenv("YIRIFI_ENV") or os.getenv("FLASK_ENV", "dev")
        return cls._normalize(env)

    @classmethod
    def _normalize(cls, env: str) -> str:
        """Normalize environment name to standard form.

        Args:
            env: Raw environment string

        Returns:
            Normalized environment: 'dev', 'uat', or 'prd'
        """
        env = env.lower()
        env = ENV_ALIASES.get(env, env)
        return env if env in VALID_ENVIRONMENTS else "dev"

    @classmethod
    def set(cls, env: str) -> None:
        """Set the environment for the current context.

        Args:
            env: Environment string ('dev', 'uat', or 'prd') or alias

        Raises:
            ValueError: If env is not a valid environment or alias
        """
        env_lower = env.lower()
        # Check if it's a valid environment or a known alias
        if env_lower not in VALID_ENVIRONMENTS and env_lower not in ENV_ALIASES:
            raise ValueError(
                f"Invalid environment: {env}. Must be one of {VALID_ENVIRONMENTS} "
                f"or aliases: {list(ENV_ALIASES.keys())}"
            )
        normalized = cls._normalize(env)
        _env_var.set(normalized)

    @classmethod
    def reset(cls) -> None:
        """Reset environment to auto-detection (clear explicit setting)."""
        _env_var.set(None)

    @classmethod
    @contextmanager
    def override(cls, env: str) -> Generator[None, None, None]:
        """Temporarily override the environment.

        Useful for testing or when you need to resolve links for a different
        environment temporarily.

        Args:
            env: Environment to use within the context

        Example:
            Environment.set('dev')
            print(Environment.get())  # 'dev'

            with Environment.override('prd'):
                print(Environment.get())  # 'prd'

            print(Environment.get())  # 'dev' (restored)
        """
        normalized = cls._normalize(env)
        if normalized not in VALID_ENVIRONMENTS:
            raise ValueError(
                f"Invalid environment: {env}. Must be one of {VALID_ENVIRONMENTS}"
            )

        token = _env_var.set(normalized)
        try:
            yield
        finally:
            _env_var.reset(token)


# Convenience functions for backwards compatibility and simpler imports
def get_environment() -> str:
    """Get the current environment. Alias for Environment.get()."""
    return Environment.get()


def set_environment(env: str) -> None:
    """Set the environment. Alias for Environment.set()."""
    Environment.set(env)
