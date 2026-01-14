"""Yirifi Ops Auth Client - Authentication library for Yirifi Ops microsites."""

from yirifi_ops_auth.client import YirifiOpsAuthClient
from yirifi_ops_auth.middleware import setup_auth_middleware, AuthMiddleware
from yirifi_ops_auth.decorators import (
    require_auth,
    require_admin,
    require_access,
    # RBAC decorators
    require_permission,
    require_any_permission,
    require_all_permissions,
    require_role,
    # Helpers
    get_current_user,
    is_authenticated,
)
from yirifi_ops_auth.models import AuthUser, VerifyResult
from yirifi_ops_auth.exceptions import AuthenticationError, AuthorizationError
from yirifi_ops_auth.local_user import (
    ensure_local_user,
    get_current_user_id,
    get_current_user_context,
    LocalUserMixin,
)

__version__ = '3.2.1'

__all__ = [
    # Client
    'YirifiOpsAuthClient',
    # Middleware
    'setup_auth_middleware',
    'AuthMiddleware',
    # Auth decorators
    'require_auth',
    'require_admin',  # deprecated
    'require_access',
    # RBAC decorators
    'require_permission',
    'require_any_permission',
    'require_all_permissions',
    'require_role',
    # Helpers
    'get_current_user',
    'is_authenticated',
    # Local user helpers
    'ensure_local_user',
    'get_current_user_id',
    'get_current_user_context',
    'LocalUserMixin',
    # Models
    'AuthUser',
    'VerifyResult',
    # Exceptions
    'AuthenticationError',
    'AuthorizationError',
]
