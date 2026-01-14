"""HTTP client for auth service communication."""
import httpx
from typing import Optional

from yirifi_ops_auth.models import AuthUser, VerifyResult
from yirifi_ops_auth.exceptions import AuthServiceError


class YirifiOpsAuthClient:
    """Client for communicating with the Yirifi Ops Auth Service."""

    def __init__(
        self,
        auth_service_url: str,
        timeout: float = 5.0,
        verify_ssl: bool = True
    ):
        """
        Initialize the auth client.

        Args:
            auth_service_url: Base URL of the auth service (e.g., 'http://localhost:5100')
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.auth_service_url = auth_service_url.rstrip('/')
        self.timeout = timeout
        self._client = httpx.Client(
            timeout=timeout,
            verify=verify_ssl
        )

    def verify(
        self,
        session_cookie: Optional[str] = None,
        api_key: Optional[str] = None,
        microsite_id: Optional[str] = None,
        app_id: Optional[str] = None,
        permission: Optional[str] = None
    ) -> VerifyResult:
        """
        Verify session cookie or API key with auth service.

        Args:
            session_cookie: Session cookie value (yirifi_ops_session)
            api_key: API key for programmatic access
            microsite_id: Optional microsite ID to check access for (deprecated, use app_id)
            app_id: Application ID to get app-specific roles/permissions
            permission: Specific permission to verify

        Returns:
            VerifyResult with validation status, user info, and permissions
        """
        if not session_cookie and not api_key:
            return VerifyResult(
                valid=False,
                error='no_credentials',
                redirect_url=f'{self.auth_service_url}/auth/login'
            )

        headers = {}
        if session_cookie:
            headers['Cookie'] = f'yirifi_ops_session={session_cookie}'
        if api_key:
            headers['X-API-Key'] = api_key

        payload = {}
        # Support both app_id (new) and microsite_id (legacy)
        if app_id:
            payload['app_id'] = app_id
        elif microsite_id:
            payload['app_id'] = microsite_id
        if permission:
            payload['permission'] = permission

        try:
            response = self._client.post(
                f'{self.auth_service_url}/api/v1/auth/verify',
                headers=headers,
                json=payload if payload else None
            )

            data = response.json()

            if data.get('valid'):
                user_data = data['user']
                access_data = data.get('access', {})

                return VerifyResult(
                    valid=True,
                    user=AuthUser(
                        user_id=user_data.get('user_id'),
                        id=user_data['id'],
                        email=user_data['email'],
                        display_name=user_data['display_name'],
                        is_admin=user_data.get('is_admin', False),
                        microsites=access_data.get('microsites', user_data.get('microsites', [])),
                        # RBAC fields
                        roles=access_data.get('roles', []),
                        permissions=access_data.get('permissions', []),
                        effective_role=access_data.get('effective_role')
                    ),
                    has_access=access_data.get('has_access', True),
                    role=access_data.get('effective_role', access_data.get('role'))
                )
            else:
                # Ensure redirect_url is absolute (prepend auth_service_url if relative)
                redirect_url = data.get('redirect_url', '/auth/login')
                if redirect_url.startswith('/'):
                    redirect_url = f'{self.auth_service_url}{redirect_url}'
                return VerifyResult(
                    valid=False,
                    error=data.get('error'),
                    redirect_url=redirect_url
                )

        except httpx.RequestError as e:
            raise AuthServiceError(f'Failed to connect to auth service: {e}')
        except Exception as e:
            raise AuthServiceError(f'Auth verification failed: {e}')

    def get_login_url(self, return_url: str = '') -> str:
        """Get the login URL with optional return URL."""
        if return_url:
            return f'{self.auth_service_url}/auth/login?return_url={return_url}'
        return f'{self.auth_service_url}/auth/login'

    def get_access_denied_url(self, app_id: str = '', return_url: str = '') -> str:
        """Get the access denied page URL with app context."""
        from urllib.parse import urlencode
        params = {}
        if app_id:
            params['app_id'] = app_id
        if return_url:
            params['return_url'] = return_url
        if params:
            return f'{self.auth_service_url}/auth/access-denied?{urlencode(params)}'
        return f'{self.auth_service_url}/auth/access-denied'

    def get_logout_url(self, return_url: str = '') -> str:
        """Get the logout URL with optional return URL."""
        if return_url:
            return f'{self.auth_service_url}/auth/logout?return_url={return_url}'
        return f'{self.auth_service_url}/auth/logout'

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
