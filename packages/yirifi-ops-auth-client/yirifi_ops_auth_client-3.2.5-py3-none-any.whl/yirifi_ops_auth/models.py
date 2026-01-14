"""Data models for auth client."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AuthUser:
    """Authenticated user information with RBAC support."""

    user_id: str  # Immutable UUID, use for storage in domain tables
    id: int  # Internal ID (kept for backward compatibility)
    email: str
    display_name: str
    is_admin: bool  # deprecated - use has_permission() instead
    microsites: list[str]

    # RBAC fields
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    effective_role: Optional[str] = None

    def has_access_to(self, microsite_id: str) -> bool:
        """Check if user has access to a microsite."""
        return microsite_id in self.microsites

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission.

        Args:
            permission: Permission code (e.g., 'report:create')

        Returns:
            True if user has the permission or wildcard '*'
        """
        # Wildcard permission grants access to everything
        if '*' in self.permissions:
            return True
        return permission in self.permissions

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role.

        Args:
            role: Role code (e.g., 'editor')

        Returns:
            True if user has the role
        """
        return role in self.roles

    def has_any_permission(self, *permissions: str) -> bool:
        """Check if user has any of the specified permissions.

        Args:
            *permissions: Permission codes to check

        Returns:
            True if user has at least one of the permissions or wildcard '*'
        """
        # Wildcard permission grants access to everything
        if '*' in self.permissions:
            return True
        return any(p in self.permissions for p in permissions)

    def has_all_permissions(self, *permissions: str) -> bool:
        """Check if user has all of the specified permissions.

        Args:
            *permissions: Permission codes to check

        Returns:
            True if user has all of the permissions or wildcard '*'
        """
        # Wildcard permission grants access to everything
        if '*' in self.permissions:
            return True
        return all(p in self.permissions for p in permissions)


@dataclass
class VerifyResult:
    """Result from auth verification."""

    valid: bool
    user: Optional[AuthUser] = None
    error: Optional[str] = None
    redirect_url: Optional[str] = None
    has_access: bool = True
    role: Optional[str] = None  # deprecated - use user.effective_role instead
