"""Tests for the local user helpers module."""

import pytest
from unittest.mock import MagicMock, patch

from yirifi_ops_auth.models import AuthUser
from yirifi_ops_auth.local_user import (
    get_current_user_id,
    get_current_user_context,
    ensure_local_user,
    LocalUserMixin,
)
from yirifi_ops_auth.exceptions import AuthenticationError


# ============================================
# Test Fixtures
# ============================================

@pytest.fixture
def mock_auth_user():
    """Create a mock authenticated user with user_id."""
    return AuthUser(
        user_id='550e8400-e29b-41d4-a716-446655440000',
        id=123,
        email='test@example.com',
        display_name='Test User',
        is_admin=False,
        microsites=['risk', 'reg'],
        roles=['viewer'],
        permissions=['read:reports'],
        effective_role='viewer'
    )


@pytest.fixture
def mock_flask_g(mock_auth_user):
    """Mock Flask's g object with current_user set."""
    mock_g = MagicMock()
    mock_g.current_user = mock_auth_user
    return mock_g


@pytest.fixture
def mock_flask_g_empty():
    """Mock Flask's g object without current_user."""
    mock_g = MagicMock(spec=[])  # No attributes by default
    return mock_g


# ============================================
# AuthUser Model Tests
# ============================================

class TestAuthUserModel:
    def test_auth_user_has_user_id_field(self, mock_auth_user):
        """Verify AuthUser includes user_id field."""
        assert hasattr(mock_auth_user, 'user_id')
        assert mock_auth_user.user_id == '550e8400-e29b-41d4-a716-446655440000'

    def test_auth_user_backward_compatibility(self, mock_auth_user):
        """Verify id field still works for backward compatibility."""
        assert hasattr(mock_auth_user, 'id')
        assert mock_auth_user.id == 123

    def test_auth_user_all_fields(self, mock_auth_user):
        """Verify all AuthUser fields are accessible."""
        assert mock_auth_user.email == 'test@example.com'
        assert mock_auth_user.display_name == 'Test User'
        assert mock_auth_user.is_admin is False
        assert 'risk' in mock_auth_user.microsites
        assert 'viewer' in mock_auth_user.roles
        assert 'read:reports' in mock_auth_user.permissions
        assert mock_auth_user.effective_role == 'viewer'

    def test_auth_user_permission_methods(self, mock_auth_user):
        """Verify permission helper methods still work."""
        assert mock_auth_user.has_permission('read:reports') is True
        assert mock_auth_user.has_permission('admin:delete') is False
        assert mock_auth_user.has_role('viewer') is True
        assert mock_auth_user.has_role('admin') is False
        assert mock_auth_user.has_access_to('risk') is True
        assert mock_auth_user.has_access_to('unknown') is False


# ============================================
# get_current_user_id Tests
# ============================================

class TestGetCurrentUserId:
    def test_returns_user_id_when_authenticated(self, mock_flask_g):
        """Verify get_current_user_id returns UUID when user is authenticated."""
        with patch('yirifi_ops_auth.local_user.g', mock_flask_g):
            user_id = get_current_user_id()
            assert user_id == '550e8400-e29b-41d4-a716-446655440000'

    def test_raises_when_no_current_user_attr(self, mock_flask_g_empty):
        """Verify AuthenticationError raised when g.current_user doesn't exist."""
        with patch('yirifi_ops_auth.local_user.g', mock_flask_g_empty):
            with pytest.raises(AuthenticationError) as exc_info:
                get_current_user_id()
            assert "No authenticated user" in str(exc_info.value)

    def test_raises_when_current_user_is_none(self):
        """Verify AuthenticationError raised when g.current_user is None."""
        mock_g = MagicMock()
        mock_g.current_user = None
        with patch('yirifi_ops_auth.local_user.g', mock_g):
            with pytest.raises(AuthenticationError):
                get_current_user_id()


# ============================================
# get_current_user_context Tests
# ============================================

class TestGetCurrentUserContext:
    def test_returns_context_dict_when_authenticated(self, mock_flask_g):
        """Verify get_current_user_context returns correct dict."""
        with patch('yirifi_ops_auth.local_user.g', mock_flask_g):
            context = get_current_user_context()
            assert context['user_id'] == '550e8400-e29b-41d4-a716-446655440000'
            assert context['display_name'] == 'Test User'
            assert context['email'] == 'test@example.com'

    def test_context_dict_has_exactly_three_keys(self, mock_flask_g):
        """Verify context dict has only user_id, display_name, email."""
        with patch('yirifi_ops_auth.local_user.g', mock_flask_g):
            context = get_current_user_context()
            assert len(context) == 3
            assert set(context.keys()) == {'user_id', 'display_name', 'email'}

    def test_raises_when_not_authenticated(self, mock_flask_g_empty):
        """Verify AuthenticationError raised when not authenticated."""
        with patch('yirifi_ops_auth.local_user.g', mock_flask_g_empty):
            with pytest.raises(AuthenticationError) as exc_info:
                get_current_user_context()
            assert "No authenticated user" in str(exc_info.value)


# ============================================
# ensure_local_user Tests
# ============================================

class TestEnsureLocalUser:
    def test_inserts_user_when_authenticated(self, mock_flask_g):
        """Verify ensure_local_user executes INSERT when user is authenticated."""
        mock_session = MagicMock()

        with patch('yirifi_ops_auth.local_user.g', mock_flask_g):
            ensure_local_user(mock_session)

        # Verify execute was called
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

        # Verify the SQL text contains expected INSERT
        call_args = mock_session.execute.call_args
        sql_text = str(call_args[0][0])
        assert 'INSERT INTO users' in sql_text
        assert 'ON CONFLICT' in sql_text
        assert 'DO NOTHING' in sql_text

    def test_passes_correct_parameters(self, mock_flask_g):
        """Verify correct parameters are passed to INSERT."""
        mock_session = MagicMock()

        with patch('yirifi_ops_auth.local_user.g', mock_flask_g):
            ensure_local_user(mock_session)

        call_args = mock_session.execute.call_args
        params = call_args[0][1]

        assert params['user_id'] == '550e8400-e29b-41d4-a716-446655440000'
        assert params['email'] == 'test@example.com'
        assert params['display_name'] == 'Test User'
        assert 'synced_at' in params
        assert 'created_at' in params

    def test_does_nothing_when_not_authenticated(self, mock_flask_g_empty):
        """Verify ensure_local_user does nothing when no user."""
        mock_session = MagicMock()

        with patch('yirifi_ops_auth.local_user.g', mock_flask_g_empty):
            ensure_local_user(mock_session)

        mock_session.execute.assert_not_called()
        mock_session.commit.assert_not_called()

    def test_does_nothing_when_current_user_is_none(self):
        """Verify ensure_local_user does nothing when current_user is None."""
        mock_g = MagicMock()
        mock_g.current_user = None
        mock_session = MagicMock()

        with patch('yirifi_ops_auth.local_user.g', mock_g):
            ensure_local_user(mock_session)

        mock_session.execute.assert_not_called()

    def test_rolls_back_on_exception(self, mock_flask_g):
        """Verify ensure_local_user rolls back on DB error."""
        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception("DB Error")

        with patch('yirifi_ops_auth.local_user.g', mock_flask_g):
            # Should not raise - silently fails
            ensure_local_user(mock_session)

        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()

    def test_silently_handles_duplicate_key(self, mock_flask_g):
        """Verify ensure_local_user handles duplicate key gracefully."""
        mock_session = MagicMock()
        # Simulate integrity error
        mock_session.execute.side_effect = Exception("duplicate key value")

        with patch('yirifi_ops_auth.local_user.g', mock_flask_g):
            # Should not raise
            ensure_local_user(mock_session)

        mock_session.rollback.assert_called_once()


# ============================================
# LocalUserMixin Tests
# ============================================

class TestLocalUserMixin:
    def test_mixin_has_required_columns(self):
        """Verify LocalUserMixin defines required column attributes."""
        assert hasattr(LocalUserMixin, 'user_id')
        assert hasattr(LocalUserMixin, 'email')
        assert hasattr(LocalUserMixin, 'display_name')
        assert hasattr(LocalUserMixin, 'is_active')
        assert hasattr(LocalUserMixin, 'synced_at')
        assert hasattr(LocalUserMixin, 'created_at')

    def test_user_id_is_primary_key(self):
        """Verify user_id column is set as primary key."""
        from sqlalchemy import Column
        user_id_col = LocalUserMixin.user_id
        assert isinstance(user_id_col, Column)
        assert user_id_col.primary_key is True


# ============================================
# Integration Tests
# ============================================

class TestIntegration:
    def test_full_auth_flow(self, mock_flask_g):
        """Test complete authentication flow with user_id."""
        with patch('yirifi_ops_auth.local_user.g', mock_flask_g):
            # 1. Get user ID for storage
            user_id = get_current_user_id()
            assert user_id is not None

            # 2. Get user context for API response
            context = get_current_user_context()
            assert context['user_id'] == user_id

            # 3. Ensure local user (would insert to DB)
            mock_session = MagicMock()
            ensure_local_user(mock_session)
            mock_session.execute.assert_called_once()

    def test_exports_from_package(self):
        """Verify all local_user exports are available from main package."""
        from yirifi_ops_auth import (
            ensure_local_user,
            get_current_user_id,
            get_current_user_context,
            LocalUserMixin,
            AuthenticationError,
        )
        assert callable(ensure_local_user)
        assert callable(get_current_user_id)
        assert callable(get_current_user_context)
        assert LocalUserMixin is not None
        assert AuthenticationError is not None
