import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from app.services.user import UserService
from app.repositories.user import UserRepository
from app.schemas.user import SignUpRequest, UserUpdateRequest, UserSelfUpdateRequest
from app.models.user import User
from fastapi import HTTPException


@pytest.mark.asyncio
class TestUserService:
    """Tests for UserService"""

    async def test_get_all_users_returns_list(self):
        """Test that get_all_users returns a list of users"""
        mock_session = AsyncMock()
        mock_users = [
            User(
                id=uuid4(),
                email="user1@test.com",
                username="user1",
                is_active=True,
                is_superuser=False,
                hashed_password="hashed",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            ),
            User(
                id=uuid4(),
                email="user2@test.com",
                username="user2",
                is_active=True,
                is_superuser=False,
                hashed_password="hashed",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            ),
        ]

        with patch.object(UserRepository, 'get_all', new_callable=AsyncMock) as mock_get_all:
            with patch.object(UserRepository, 'count', new_callable=AsyncMock) as mock_count:
                mock_get_all.return_value = mock_users
                mock_count.return_value = 2

                service = UserService(mock_session)
                result = await service.get_all_users(skip=0, limit=100)

                assert result.total == 2
                assert len(result.users) == 2
                mock_get_all.assert_called_once_with(skip=0, limit=100)
                mock_count.assert_called_once()

    async def test_get_all_users_empty_database(self):
        """Test get_all_users when database is empty"""
        mock_session = AsyncMock()

        with patch.object(UserRepository, 'get_all', new_callable=AsyncMock) as mock_get_all:
            with patch.object(UserRepository, 'count', new_callable=AsyncMock) as mock_count:
                mock_get_all.return_value = []
                mock_count.return_value = 0

                service = UserService(mock_session)
                result = await service.get_all_users(skip=0, limit=100)

                assert result.total == 0
                assert len(result.users) == 0

    async def test_get_user_by_id_success(self):
        """Test getting user by ID successfully"""
        mock_session = AsyncMock()
        user_id = uuid4()
        mock_user = User(
            id=user_id,
            email="test@test.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(UserRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = mock_user

            service = UserService(mock_session)
            result = await service.get_user_by_id(user_id)

            assert result.id == user_id
            assert result.email == "test@test.com"
            assert result.username == "testuser"
            mock_get_by_id.assert_called_once_with(user_id)

    async def test_get_user_by_id_not_found(self):
        """Test getting user by ID when user doesn't exist raises 404"""
        mock_session = AsyncMock()
        user_id = uuid4()

        with patch.object(UserRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = None

            service = UserService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.get_user_by_id(user_id)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "User not found"

    async def test_create_user_success(self):
        """Test creating a new user successfully"""
        mock_session = AsyncMock()
        user_data = SignUpRequest(
            email="newuser@test.com",
            username="newuser",
            password="password123"
        )

        created_user = User(
            id=uuid4(),
            email=user_data.email,
            username=user_data.username,
            hashed_password="hashed_password",
            is_active=True,
            is_superuser=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(UserRepository, 'get_by_email', new_callable=AsyncMock) as mock_get_email:
            with patch.object(UserRepository, 'get_by_username', new_callable=AsyncMock) as mock_get_username:
                with patch.object(UserRepository, 'create', new_callable=AsyncMock) as mock_create:
                    with patch('app.services.user.hash_password') as mock_hash:
                        mock_get_email.return_value = None
                        mock_get_username.return_value = None
                        mock_hash.return_value = "hashed_password"
                        mock_create.return_value = created_user

                        service = UserService(mock_session)
                        result = await service.create_user(user_data)

                        assert result.email == "newuser@test.com"
                        assert result.username == "newuser"
                        mock_hash.assert_called_once_with("password123")
                        mock_create.assert_called_once()

    async def test_update_user_success(self):
        """Test updating user successfully"""
        mock_session = AsyncMock()
        user_id = uuid4()

        existing_user = User(
            id=user_id,
            email="old@test.com",
            username="olduser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        update_data = UserUpdateRequest(
            email="updated@test.com",
            username="updateduser"
        )

        updated_user = User(
            id=user_id,
            email="updated@test.com",
            username="updateduser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(UserRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_by_id:
            with patch.object(UserRepository, 'get_by_email', new_callable=AsyncMock) as mock_get_by_email:
                with patch.object(UserRepository, 'get_by_username', new_callable=AsyncMock) as mock_get_by_username:
                    with patch.object(UserRepository, 'update', new_callable=AsyncMock) as mock_update:
                        mock_get_by_id.return_value = existing_user
                        mock_get_by_email.return_value = None
                        mock_get_by_username.return_value = None
                        mock_update.return_value = updated_user

                        service = UserService(mock_session)
                        result = await service.update_user(user_id, update_data)

                        assert result.email == "updated@test.com"
                        assert result.username == "updateduser"

    async def test_update_user_with_password(self):
        """Test updating user with new password"""
        mock_session = AsyncMock()
        user_id = uuid4()

        existing_user = User(
            id=user_id,
            email="test@test.com",
            username="testuser",
            hashed_password="old_hash",
            is_active=True,
            is_superuser=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        update_data = UserUpdateRequest(password="newpassword123")

        with patch.object(UserRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_by_id:
            with patch.object(UserRepository, 'update', new_callable=AsyncMock) as mock_update:
                mock_get_by_id.return_value = existing_user

                existing_user.hashed_password = "some_new_hash"
                mock_update.return_value = existing_user

                service = UserService(mock_session)
                result = await service.update_user(user_id, update_data)

                mock_update.assert_called_once()

    async def test_update_self_username_only(self):
        """Test user updating their own username"""
        mock_session = AsyncMock()
        user_id = uuid4()

        current_user = User(
            id=user_id,
            email="test@test.com",
            username="oldusername",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        update_data = UserSelfUpdateRequest(username="newusername")

        updated_user = User(
            id=user_id,
            email="test@test.com",
            username="newusername",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(UserRepository, 'get_by_username', new_callable=AsyncMock) as mock_get_by_username:
            with patch.object(UserRepository, 'update', new_callable=AsyncMock) as mock_update:
                mock_get_by_username.return_value = None
                mock_update.return_value = updated_user

                service = UserService(mock_session)
                result = await service.update_self(current_user, update_data)

                assert result.username == "newusername"
                mock_update.assert_called_once()

    async def test_update_self_password_only(self):
        """Test user updating their own password"""
        mock_session = AsyncMock()
        user_id = uuid4()

        current_user = User(
            id=user_id,
            email="test@test.com",
            username="testuser",
            hashed_password="old_hash",
            is_active=True,
            is_superuser=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        update_data = UserSelfUpdateRequest(password="newpassword123")

        updated_user = User(
            id=user_id,
            email="test@test.com",
            username="testuser",
            hashed_password="new_hashed_password",
            is_active=True,
            is_superuser=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(UserRepository, 'update', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = updated_user

            service = UserService(mock_session)
            result = await service.update_self(current_user, update_data)

            mock_update.assert_called_once()

    async def test_delete_user_success(self):
        """Test deleting user successfully"""
        mock_session = AsyncMock()
        user_id = uuid4()

        existing_user = User(
            id=user_id,
            email="test@test.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(UserRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_by_id:
            with patch.object(UserRepository, 'delete', new_callable=AsyncMock) as mock_delete:
                mock_get_by_id.return_value = existing_user
                mock_delete.return_value = None

                service = UserService(mock_session)
                result = await service.delete_user(user_id)

                assert result is None
                mock_delete.assert_called_once_with(existing_user)

    async def test_delete_user_not_found(self):
        """Test deleting non-existent user raises 404"""
        mock_session = AsyncMock()
        user_id = uuid4()

        with patch.object(UserRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = None

            service = UserService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.delete_user(user_id)

            assert exc_info.value.status_code == 404
