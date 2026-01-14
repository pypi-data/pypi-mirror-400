"""Custom exceptions for auth client."""


class AuthClientError(Exception):
    """Base exception for auth client errors."""

    pass


class AuthenticationError(AuthClientError):
    """Authentication failed - user not logged in or invalid credentials."""

    def __init__(self, message: str = 'Authentication required', redirect_url: str = None):
        super().__init__(message)
        self.message = message
        self.redirect_url = redirect_url


class AuthorizationError(AuthClientError):
    """Authorization failed - user doesn't have required permissions."""

    def __init__(self, message: str = 'Access denied'):
        super().__init__(message)
        self.message = message


class AuthServiceError(AuthClientError):
    """Error communicating with auth service."""

    def __init__(self, message: str = 'Auth service unavailable'):
        super().__init__(message)
        self.message = message
