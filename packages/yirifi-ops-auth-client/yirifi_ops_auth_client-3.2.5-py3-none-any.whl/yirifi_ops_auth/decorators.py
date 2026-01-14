"""Authentication decorators for Flask routes."""
from functools import wraps
from flask import g

from yirifi_ops_auth.exceptions import AuthenticationError, AuthorizationError


def require_auth(f):
    """
    Decorator to require authentication on a route.

    The middleware already handles authentication, but this decorator
    provides an explicit check for routes that must have a user.

    Example:
        @app.route('/profile')
        @require_auth
        def profile():
            return f"Hello {g.current_user.display_name}"
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user is None:
            raise AuthenticationError('Authentication required')
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    """
    Decorator to require admin privileges.

    DEPRECATED: Use @require_permission('admin:access') or @require_role('super_admin') instead.

    Example:
        @app.route('/admin')
        @require_admin
        def admin_panel():
            return "Admin only content"
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user is None:
            raise AuthenticationError('Authentication required')
        # Use role check instead of deprecated is_admin field
        if not g.current_user.has_role('super_admin'):
            raise AuthorizationError('Admin access required')
        return f(*args, **kwargs)
    return decorated


def require_permission(permission: str):
    """
    Decorator factory to require a specific permission.

    Args:
        permission: Permission code to require (e.g., 'report:create')

    Example:
        @app.route('/reports', methods=['POST'])
        @require_permission('report:create')
        def create_report():
            # User has report:create permission
            return create_new_report(request.json)
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'current_user') or g.current_user is None:
                raise AuthenticationError('Authentication required')

            if not g.current_user.has_permission(permission):
                raise AuthorizationError(f'Permission denied: {permission}')

            return f(*args, **kwargs)
        return decorated
    return decorator


def require_any_permission(*permissions: str):
    """
    Decorator factory to require at least one of the specified permissions.

    Args:
        *permissions: Permission codes to check

    Example:
        @require_any_permission('report:read', 'report:create')
        def view_reports():
            return get_reports()
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'current_user') or g.current_user is None:
                raise AuthenticationError('Authentication required')

            if not g.current_user.has_any_permission(*permissions):
                raise AuthorizationError(
                    f'Permission denied. Required one of: {", ".join(permissions)}'
                )

            return f(*args, **kwargs)
        return decorated
    return decorator


def require_all_permissions(*permissions: str):
    """
    Decorator factory to require all of the specified permissions.

    Args:
        *permissions: Permission codes to check

    Example:
        @require_all_permissions('report:read', 'data:export')
        def export_report():
            return generate_export()
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'current_user') or g.current_user is None:
                raise AuthenticationError('Authentication required')

            if not g.current_user.has_all_permissions(*permissions):
                missing = [p for p in permissions if not g.current_user.has_permission(p)]
                raise AuthorizationError(
                    f'Permission denied. Missing: {", ".join(missing)}'
                )

            return f(*args, **kwargs)
        return decorated
    return decorator


def require_role(role: str):
    """
    Decorator factory to require a specific role.

    Note: Prefer using @require_permission() over @require_role() as it
    provides more granular access control.

    Args:
        role: Role code to require (e.g., 'admin', 'editor')

    Example:
        @require_role('admin')
        def admin_dashboard():
            return render_template('admin/dashboard.html')
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'current_user') or g.current_user is None:
                raise AuthenticationError('Authentication required')

            if not g.current_user.has_role(role):
                raise AuthorizationError(f'Role required: {role}')

            return f(*args, **kwargs)
        return decorated
    return decorator


def require_access(microsite_id: str):
    """
    Decorator factory to require access to a specific microsite.

    This is useful when a route needs access to a different microsite
    than the one the app is registered under.

    Example:
        @app.route('/cross-site-data')
        @require_access('other-microsite')
        def cross_site():
            return "Data from other microsite"
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'current_user') or g.current_user is None:
                raise AuthenticationError('Authentication required')
            if not g.current_user.has_access_to(microsite_id):
                raise AuthorizationError(f'Access denied to {microsite_id}')
            return f(*args, **kwargs)
        return decorated
    return decorator


def get_current_user():
    """
    Get the current authenticated user.

    Returns:
        AuthUser or None if not authenticated

    Example:
        user = get_current_user()
        if user:
            print(f"Logged in as {user.email}")
    """
    return getattr(g, 'current_user', None)


def is_authenticated() -> bool:
    """
    Check if the current request is authenticated.

    Returns:
        True if user is authenticated
    """
    return hasattr(g, 'current_user') and g.current_user is not None
