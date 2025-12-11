import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from app.services.auth import AuthService
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.models.user import User


@pytest.mark.asyncio
class TestAuthService:
    """Tests for AuthService"""

    async def test_login_success(self):
        """Test successful login with correct credentials"""
        mock_session = AsyncMock()

        login_data = LoginRequest(
            email="user@test.com",
            password="password123"
        )

        mock_user = User(
            id=uuid4(),
            email="user@test.com",
            username="testuser",
            hashed_password="$2b$12$hashed_password",
            is_active=True,
            is_superuser=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(UserRepository, 'get_by_email', new_callable=AsyncMock) as mock_get_email:
            with patch('app.services.auth.verify_password') as mock_verify:
                with patch('app.services.auth.create_access_token') as mock_access:
                    with patch('app.services.auth.create_refresh_access_token') as mock_refresh:
                        mock_get_email.return_value = mock_user
                        mock_verify.return_value = True
                        mock_access.return_value = "access_token_123"
                        mock_refresh.return_value = "refresh_token_456"

                        service = AuthService(mock_session)
                        result = await service.login(login_data)

                        assert isinstance(result, TokenResponse)
                        assert result.access_token == "access_token_123"
                        assert result.refresh_token == "refresh_token_456"
                        assert result.token_type == "bearer"

                        mock_get_email.assert_called_once_with("user@test.com")
                        mock_verify.assert_called_once_with("password123", "$2b$12$hashed_password")
                        mock_access.assert_called_once_with(data={"sub": "user@test.com"})
                        mock_refresh.assert_called_once_with(data={"sub": "user@test.com"})

    async def test_login_user_not_found(self):
        """Test login fails when user doesn't exist"""
        mock_session = AsyncMock()

        login_data = LoginRequest(
            email="nonexistent@test.com",
            password="password123"
        )

        with patch.object(UserRepository, 'get_by_email', new_callable=AsyncMock) as mock_get_email:
            mock_get_email.return_value = None

            service = AuthService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.login(login_data)

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Incorrect email or password"

    async def test_login_incorrect_password(self):
        """Test login fails with incorrect password"""
        mock_session = AsyncMock()

        login_data = LoginRequest(
            email="user@test.com",
            password="wrong_password"
        )

        mock_user = User(
            id=uuid4(),
            email="user@test.com",
            username="testuser",
            hashed_password="$2b$12$hashed_password",
            is_active=True,
            is_superuser=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(UserRepository, 'get_by_email', new_callable=AsyncMock) as mock_get_email:
            with patch('app.services.auth.verify_password') as mock_verify:
                mock_get_email.return_value = mock_user
                mock_verify.return_value = False

                service = AuthService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.login(login_data)

                assert exc_info.value.status_code == 401
                assert exc_info.value.detail == "Incorrect email or password"

    async def test_login_inactive_user(self):
        """Test login fails for inactive user"""
        mock_session = AsyncMock()

        login_data = LoginRequest(
            email="user@test.com",
            password="password123"
        )

        mock_user = User(
            id=uuid4(),
            email="user@test.com",
            username="testuser",
            hashed_password="$2b$12$hashed_password",
            is_active=False,
            is_superuser=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(UserRepository, 'get_by_email', new_callable=AsyncMock) as mock_get_email:
            with patch('app.services.auth.verify_password') as mock_verify:
                mock_get_email.return_value = mock_user
                mock_verify.return_value = True

                service = AuthService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.login(login_data)

                assert exc_info.value.status_code == 400
                assert exc_info.value.detail == "Inactive user"

    async def test_login_returns_token_response(self):
        """Test login returns proper TokenResponse structure"""
        mock_session = AsyncMock()

        login_data = LoginRequest(
            email="user@test.com",
            password="password123"
        )

        mock_user = User(
            id=uuid4(),
            email="user@test.com",
            username="testuser",
            hashed_password="$2b$12$hashed_password",
            is_active=True,
            is_superuser=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(UserRepository, 'get_by_email', new_callable=AsyncMock) as mock_get_email:
            with patch('app.services.auth.verify_password') as mock_verify:
                with patch('app.services.auth.create_access_token') as mock_access:
                    with patch('app.services.auth.create_refresh_access_token') as mock_refresh:
                        mock_get_email.return_value = mock_user
                        mock_verify.return_value = True
                        mock_access.return_value = "test_access_token"
                        mock_refresh.return_value = "test_refresh_token"

                        service = AuthService(mock_session)
                        result = await service.login(login_data)

                        assert hasattr(result, 'access_token')
                        assert hasattr(result, 'refresh_token')
                        assert hasattr(result, 'token_type')
                        assert result.token_type == "bearer"

    async def test_refresh_token_success(self):
        """Test successful token refresh with valid refresh token"""
        mock_session = AsyncMock()

        mock_user = User(
            id=uuid4(),
            email="user@test.com",
            username="testuser",
            hashed_password="$2b$12$hashed_password",
            is_active=True,
            is_superuser=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_payload = {
            "sub": "user@test.com",
            "type": "refresh"
        }

        with patch.object(UserRepository, 'get_by_email', new_callable=AsyncMock) as mock_get_email:
            with patch('app.core.security.decode_refresh_token') as mock_decode:
                with patch('app.services.auth.create_access_token') as mock_access:
                    with patch('app.services.auth.create_refresh_access_token') as mock_refresh:
                        mock_decode.return_value = mock_payload
                        mock_get_email.return_value = mock_user
                        mock_access.return_value = "new_access_token"
                        mock_refresh.return_value = "new_refresh_token"

                        service = AuthService(mock_session)
                        result = await service.refresh_access_token("old_refresh_token")

                        assert isinstance(result, TokenResponse)
                        assert result.access_token == "new_access_token"
                        assert result.refresh_token == "new_refresh_token"

                        mock_decode.assert_called_once_with("old_refresh_token")
                        mock_get_email.assert_called_once_with("user@test.com")

    async def test_refresh_token_invalid_type(self):
        """Test refresh fails with wrong token type"""
        mock_session = AsyncMock()

        mock_payload = {
            "sub": "user@test.com",
            "type": "access"
        }

        with patch('app.core.security.decode_refresh_token') as mock_decode:
            mock_decode.return_value = mock_payload

            service = AuthService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.refresh_access_token("invalid_token")

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid refresh token"

    async def test_refresh_token_no_email(self):
        """Test refresh fails when token has no email (sub)"""
        mock_session = AsyncMock()

        mock_payload = {
            "type": "refresh"
        }

        with patch('app.core.security.decode_refresh_token') as mock_decode:
            mock_decode.return_value = mock_payload

            service = AuthService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.refresh_access_token("token_without_email")

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid refresh token"

    async def test_refresh_token_user_not_found(self):
        """Test refresh fails when user doesn't exist"""
        mock_session = AsyncMock()

        mock_payload = {
            "sub": "nonexistent@test.com",
            "type": "refresh"
        }

        with patch.object(UserRepository, 'get_by_email', new_callable=AsyncMock) as mock_get_email:
            with patch('app.core.security.decode_refresh_token') as mock_decode:
                mock_decode.return_value = mock_payload
                mock_get_email.return_value = None

                service = AuthService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.refresh_access_token("valid_token")

                assert exc_info.value.status_code == 401
                assert exc_info.value.detail == "User not found"

    async def test_refresh_token_inactive_user(self):
        """Test refresh fails for inactive user"""
        mock_session = AsyncMock()

        mock_user = User(
            id=uuid4(),
            email="user@test.com",
            username="testuser",
            hashed_password="$2b$12$hashed_password",
            is_active=False,
            is_superuser=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_payload = {
            "sub": "user@test.com",
            "type": "refresh"
        }

        with patch.object(UserRepository, 'get_by_email', new_callable=AsyncMock) as mock_get_email:
            with patch('app.core.security.decode_refresh_token') as mock_decode:
                mock_decode.return_value = mock_payload
                mock_get_email.return_value = mock_user

                service = AuthService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.refresh_access_token("valid_token")

                assert exc_info.value.status_code == 400
                assert exc_info.value.detail == "Inactive user"

    async def test_refresh_token_null_payload(self):
        """Test refresh fails when decode returns None"""
        mock_session = AsyncMock()

        with patch('app.core.security.decode_refresh_token') as mock_decode:
            mock_decode.return_value = None

            service = AuthService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.refresh_access_token("malformed_token")

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid refresh token"
