"""
Local User Helpers

Provides utilities for microsites to manage local user tables that sync
from the central auth service.

Usage:
    from yirifi_ops_auth.local_user import ensure_local_user, get_current_user_id

    @app.before_request
    def before_request():
        ensure_local_user(db.session)

    @app.route('/api/chat', methods=['POST'])
    @require_auth
    def create_chat():
        chat = ChatHistory(user_id=get_current_user_id(), ...)
"""

from flask import g
from sqlalchemy import text
from datetime import datetime, timezone

from yirifi_ops_auth.exceptions import AuthenticationError


def get_current_user_id() -> str:
    """
    Get the current user's immutable ID for storage in domain tables.

    Returns:
        str: UUID string of the current user

    Raises:
        AuthenticationError: If no user is authenticated
    """
    if not hasattr(g, 'current_user') or not g.current_user:
        raise AuthenticationError("No authenticated user")
    return g.current_user.user_id


def get_current_user_context() -> dict:
    """
    Get the current user's display info for API responses.

    Returns:
        dict: User info including user_id, display_name, email

    Raises:
        AuthenticationError: If no user is authenticated
    """
    if not hasattr(g, 'current_user') or not g.current_user:
        raise AuthenticationError("No authenticated user")

    user = g.current_user
    return {
        'user_id': user.user_id,
        'display_name': user.display_name,
        'email': user.email
    }


def ensure_local_user(db_session):
    """
    Ensure current user exists in local users table.

    This should be called in a before_request hook after auth middleware
    sets g.current_user. It handles the case where a new user logs in
    before the daily sync has run.

    The INSERT uses ON CONFLICT DO NOTHING because:
    - If user exists, sync job keeps data fresh
    - If user is new, this creates the record
    - We don't update on login to avoid overwriting sync data

    Args:
        db_session: SQLAlchemy session (e.g., db.session)
    """
    if not hasattr(g, 'current_user') or not g.current_user:
        return

    user = g.current_user
    try:
        db_session.execute(text("""
            INSERT INTO users (user_id, email, display_name, is_active, synced_at, created_at)
            VALUES (:user_id, :email, :display_name, true, :synced_at, :created_at)
            ON CONFLICT (user_id) DO NOTHING
        """), {
            'user_id': user.user_id,
            'email': user.email,
            'display_name': user.display_name,
            'synced_at': datetime.now(timezone.utc),
            'created_at': datetime.now(timezone.utc)
        })
        db_session.commit()
    except Exception:
        db_session.rollback()
        # Silently fail - sync job will handle it
        pass


class LocalUserMixin:
    """
    Mixin for the local users table model.

    Usage:
        from yirifi_ops_auth.local_user import LocalUserMixin

        class User(db.Model, LocalUserMixin):
            __tablename__ = 'users'

            # Additional fields specific to this microsite
            preferences = db.Column(db.JSON, default={})
    """
    from sqlalchemy import Column, String, Boolean, DateTime
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.sql import func

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String(255), nullable=False)
    display_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    synced_at = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
