"""Flask middleware for authentication."""
from flask import Flask, request, redirect, g, current_app
from typing import Optional

from yirifi_ops_auth.client import YirifiOpsAuthClient
from yirifi_ops_auth.exceptions import AuthenticationError, AuthorizationError, AuthServiceError


class AuthMiddleware:
    """Authentication middleware for Flask applications with RBAC support."""

    def __init__(
        self,
        app: Flask,
        auth_client: YirifiOpsAuthClient,
        microsite_id: str = None,
        app_id: str = None,
        excluded_paths: Optional[list[str]] = None,
        excluded_prefixes: Optional[list[str]] = None,
        require_app_access: bool = True
    ):
        """
        Initialize auth middleware.

        Args:
            app: Flask application
            auth_client: YirifiOpsAuthClient instance
            microsite_id: ID of this microsite (deprecated, use app_id)
            app_id: Application ID for RBAC (e.g., 'sidebyside')
            excluded_paths: Exact paths to exclude from auth (e.g., ['/health'])
            excluded_prefixes: Path prefixes to exclude (e.g., ['/api/v1/health'])
            require_app_access: If True (default), require user to have explicit role
                              assignment in this app. Set to False only during RBAC
                              migration to allow any authenticated user temporarily.
        """
        self.app = app
        self.auth_client = auth_client
        # Support both app_id (new) and microsite_id (legacy)
        self.app_id = app_id or microsite_id
        self.microsite_id = self.app_id  # Keep for backward compatibility
        self.require_app_access = require_app_access
        self.excluded_paths = excluded_paths or []
        # Default exclusions - always included
        default_prefixes = [
            '/api/v1/health',
            '/static',
            '/favicon.ico',
            # API documentation - allow public access for tooling
            '/api/v1/swagger.json',
            '/api/v1/openapi.json',
            '/api/docs',
            '/api/v1/docs',
            '/swagger.json',
            '/openapi.json',
        ]
        # Merge app-specific prefixes with defaults (app prefixes take priority)
        if excluded_prefixes:
            self.excluded_prefixes = list(set(default_prefixes + excluded_prefixes))
        else:
            self.excluded_prefixes = default_prefixes

        # Store on app for access in routes
        app.auth_client = auth_client
        app.microsite_id = self.app_id  # Legacy
        app.app_id = self.app_id  # New

        # Register middleware
        app.before_request(self._authenticate_request)

        # Register error handlers
        self._register_error_handlers()

    def _is_excluded(self, path: str) -> bool:
        """Check if path should be excluded from authentication."""
        if path in self.excluded_paths:
            return True
        for prefix in self.excluded_prefixes:
            if path.startswith(prefix):
                return True
        return False

    def _authenticate_request(self):
        """Authenticate incoming request.

        Note: Returns responses directly instead of raising exceptions because
        Flask's @errorhandler doesn't catch exceptions from before_request hooks.
        """
        # Skip excluded paths
        if self._is_excluded(request.path):
            return None

        # Get credentials
        session_cookie = request.cookies.get('yirifi_ops_session')
        api_key = request.headers.get('X-API-Key')

        # No credentials
        if not session_cookie and not api_key:
            return self._handle_unauthenticated()

        # Verify with auth service (pass app_id for RBAC)
        try:
            result = self.auth_client.verify(
                session_cookie=session_cookie,
                api_key=api_key,
                app_id=self.app_id
            )
        except AuthServiceError as e:
            # Auth service unavailable - fail open or closed based on config
            if current_app.config.get('AUTH_FAIL_OPEN', False):
                g.current_user = None
                g.auth_method = None
                return None
            # Return error response directly
            return self._handle_auth_service_error(e.message)

        # Invalid credentials
        if not result.valid:
            if api_key:
                # API request - return 401 directly
                return self._make_auth_error_response(result.error or 'Invalid API key')
            else:
                # Browser request - redirect to login
                return self._handle_unauthenticated(result.redirect_url)

        # Check app access (only if require_app_access is enabled)
        if self.require_app_access and not result.has_access:
            return self._handle_access_denied(f'Access denied to {self.app_id}')

        # Store user in request context
        g.current_user = result.user
        g.auth_method = 'api_key' if api_key else 'session'
        g.has_app_access = result.has_access  # Store for route-level checks

        return None

    def _is_api_request(self) -> bool:
        """Detect if this is an API request (should get JSON errors, not redirects)."""
        # Explicit API key header
        if request.headers.get('X-API-Key'):
            return True
        # JSON content type
        if request.is_json:
            return True
        # Accept header prefers JSON
        accept = request.headers.get('Accept', '')
        if 'application/json' in accept and 'text/html' not in accept:
            return True
        # API path patterns (swagger, openapi, etc.)
        path = request.path.lower()
        if any(pattern in path for pattern in ['/api/', 'swagger', 'openapi', '.json']):
            return True
        return False

    def _handle_unauthenticated(self, redirect_url: str = None):
        """Handle unauthenticated request."""
        # Check if API request - return JSON error instead of redirect
        if self._is_api_request():
            return self._make_auth_error_response('Authentication required')

        # Browser request - redirect to login
        return_url = request.url
        login_url = redirect_url or self.auth_client.get_login_url(return_url)
        return redirect(login_url)

    def _make_auth_error_response(self, message: str):
        """Create a 401 JSON error response for API requests."""
        from flask import jsonify, make_response
        response = make_response(jsonify({
            'success': False,
            'error': {
                'code': 'AUTHENTICATION_REQUIRED',
                'message': message
            }
        }), 401)
        return response

    def _handle_access_denied(self, message: str):
        """Handle access denied - user authenticated but lacks permission."""
        if self._is_api_request():
            from flask import jsonify, make_response
            response = make_response(jsonify({
                'success': False,
                'error': {
                    'code': 'ACCESS_DENIED',
                    'message': message
                }
            }), 403)
            return response
        # Browser request - redirect to access denied page
        access_denied_url = self.auth_client.get_access_denied_url(
            app_id=self.app_id,
            return_url=request.url
        )
        return redirect(access_denied_url)

    def _handle_auth_service_error(self, message: str):
        """Handle auth service unavailable error."""
        from flask import jsonify, make_response, render_template_string
        if self._is_api_request():
            response = make_response(jsonify({
                'success': False,
                'error': {
                    'code': 'AUTH_SERVICE_ERROR',
                    'message': 'Authentication service unavailable'
                }
            }), 503)
            return response
        # Browser request - show error page
        error_html = """
        <!DOCTYPE html>
        <html><head><title>Service Unavailable</title></head>
        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>Service Temporarily Unavailable</h1>
            <p>The authentication service is currently unavailable. Please try again later.</p>
        </body></html>
        """
        return make_response(render_template_string(error_html), 503)

    def _register_error_handlers(self):
        """Register error handlers for auth exceptions."""

        @self.app.errorhandler(AuthenticationError)
        def handle_auth_error(error):
            if self._is_api_request():
                return {
                    'success': False,
                    'error': {
                        'code': 'AUTHENTICATION_REQUIRED',
                        'message': error.message
                    }
                }, 401
            return redirect(error.redirect_url or self.auth_client.get_login_url(request.url))

        @self.app.errorhandler(AuthorizationError)
        def handle_authz_error(error):
            if self._is_api_request():
                return {
                    'success': False,
                    'error': {
                        'code': 'ACCESS_DENIED',
                        'message': error.message
                    }
                }, 403
            # Browser request - redirect to access denied page
            access_denied_url = self.auth_client.get_access_denied_url(
                app_id=self.app_id,
                return_url=request.url
            )
            return redirect(access_denied_url)


def setup_auth_middleware(
    app: Flask,
    auth_client: YirifiOpsAuthClient,
    microsite_id: str,
    **kwargs
) -> AuthMiddleware:
    """
    Set up authentication middleware for a Flask app.

    Args:
        app: Flask application
        auth_client: YirifiOpsAuthClient instance
        microsite_id: ID of this microsite
        **kwargs: Additional options passed to AuthMiddleware

    Returns:
        Configured AuthMiddleware instance

    Example:
        from yirifi_ops_auth import YirifiOpsAuthClient, setup_auth_middleware

        def create_app():
            app = Flask(__name__)

            auth_client = YirifiOpsAuthClient(app.config['AUTH_SERVICE_URL'])
            setup_auth_middleware(app, auth_client, microsite_id='sidebyside')

            return app
    """
    return AuthMiddleware(app, auth_client, microsite_id, **kwargs)
