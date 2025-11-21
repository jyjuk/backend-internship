import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import (
    SignUpRequest,
    UserUpdateRequest,
    User as UserSchema,
    UserDetail,
    UserList,
)
from app.schemas.user import UserSelfUpdateRequest
from app.core.security import hash_password

logger = logging.getLogger(__name__)


class UserService:
    """Service for user logic"""

    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> UserList:
        """Get all users"""
        try:
            users = await self.repository.get_all(skip=skip, limit=limit)
            total = await self.repository.count()

            logger.info(f"Retrieved {len(users)} users (total: {total})")

            return UserList(users=[UserSchema.model_validate(user) for user in users], total=total)
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve users")

    async def get_user_by_id(self, user_id: UUID) -> UserDetail:
        """get user by id"""
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User not found: {user_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            logger.info(f"Retrieved user: {user_id}")
            return UserDetail.model_validate(user)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve user")

    async def create_user(self, data: SignUpRequest) -> UserDetail:
        """Create new user"""
        try:
            existing_user = await self.repository.get_by_email(data.email)
            if existing_user:
                logger.warning(f"User creation failed: email already exist - {data.email}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

            existing_user = await self.repository.get_by_username(data.username)
            if existing_user:
                logger.warning(f"User creation failed: username already exist - {data.username}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

            hashed_password = hash_password(data.password)
            user = User(email=data.email, username=data.username, hashed_password=hashed_password)
            created_user = await self.repository.create(user)
            logger.info(f"User created: {created_user.id} - {created_user.email}")

            return UserDetail.model_validate(created_user)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

    async def update_user(self, user_id: UUID, data: UserUpdateRequest) -> UserDetail:
        """Update user"""
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User update failed: user not found - {user_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            if data.email is not None:
                existing_user = await self.repository.get_by_email(data.email)
                if existing_user and existing_user.id != user_id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exist")
                user.email = data.email
            if data.username is not None:
                existing_user = await self.repository.get_by_username(data.username)
                if existing_user and existing_user.id != user_id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
                user.username = data.username

            if data.password is not None:
                user.hashed_password = hash_password(data.password)
            if data.is_active is not None:
                user.is_active = data.is_active

            updated_user = await self.repository.update(user)
            logger.info(f"User updated: {updated_user.id}")

            return UserDetail.model_validate(updated_user)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")

    async def delete_user(self, user_id: UUID) -> None:
        """Delete user"""
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User deletion failed: user not found - {user_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            await self.repository.delete(user)
            logger.info(f"User deleted - {user_id}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user")

    async def update_self(self, current_user: User, data: UserSelfUpdateRequest) -> UserDetail:
        """Update current user's own profile (username and/or password only)"""
        try:
            # Використовуємо self.repository замість self.user_repository
            if data.username is not None:
                existing_user = await self.repository.get_by_username(data.username)
                if existing_user and existing_user.id != current_user.id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
                current_user.username = data.username

            if data.password is not None:
                current_user.hashed_password = hash_password(data.password)

            updated_user = await self.repository.update(current_user)
            logger.info(f"User {current_user.id} updated their own profile")
            return UserDetail.model_validate(updated_user)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating own profile: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update profile")

    async def delete_self(self, current_user: User) -> None:
        """Delete current user's own profile"""
        try:
            await self.repository.delete(current_user)
            logger.info(f"User {current_user.id} deleted their own profile")
        except Exception as e:
            logger.error(f"Error deleting own profile: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete profile")
