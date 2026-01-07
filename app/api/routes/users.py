import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional
from app.services.user import UserService
from app.schemas.user import (SignUpRequest, UserUpdateRequest, UserDetail, UserList, UserSelfUpdateRequest)
from app.schemas.company import CompanyList
from app.models.user import User
from app.services.quiz_attempt_service import QuizAttemptService
from app.schemas.quiz import UserSystemStats

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/", response_model=UserList)
async def get_users(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=100, description="Maximum numbers of records"),
        db: AsyncSession = Depends(get_db)
):
    """Get all users"""
    service = UserService(db)
    return await service.get_all_users(skip=skip, limit=limit)


@router.get("/me", response_model=UserDetail, summary="Get own profile")
async def get_own_profile(
        current_user: User = Depends(get_current_user),
):
    """Get current user's profile"""
    return current_user


@router.put("/me", response_model=UserDetail, summary="Update own profile")
async def update_own_profile(
        data: UserSelfUpdateRequest,
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
):
    """Update current user's username and/or password"""
    return await user_service.update_self(current_user, data)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="Delete own profile")
async def delete_own_profile(
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
):
    """Delete current user's profile"""
    await user_service.delete_self(current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{user_id}", response_model=UserDetail)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get user by ID"""
    service = UserService(db)
    return await service.get_user_by_id(user_id)


@router.post("/", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
async def create_user(
        data: SignUpRequest, db: AsyncSession = Depends(get_db)
):
    """Create new user"""
    service = UserService(db)
    return await service.create_user(data)


@router.put("/{user_id}", response_model=UserDetail)
async def update_user(user_id: UUID, data: UserUpdateRequest, db: AsyncSession = Depends(get_db)):
    """Update user"""
    service = UserService(db)
    return await service.update_user(user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete user"""
    service = UserService(db)
    await service.delete_user(user_id)


@router.get("/{user_id}/companies", response_model=CompanyList)
async def get_user_companies(
        user_id: UUID,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
        current_user: Optional[User] = Depends(get_current_user_optional),
        db: AsyncSession = Depends(get_db)
):
    """
    Get user's companies with visibility rules:
    - Own profile: returns ALL companies (public + private)
    - Other user's profile: returns ONLY public companies
    - Not authenticated: returns ONLY public companies
    """
    from app.services.company import CompanyService
    service = CompanyService(db)

    current_user_id = current_user.id if current_user else None
    return await service.get_user_companies_visible(user_id, current_user_id, skip, limit)


@router.get("/me/quiz-stats", response_model=UserSystemStats)
async def get_my_quiz_stats(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get my quiz statistics across all companies"""
    service = QuizAttemptService(db)
    return await service.get_user_system_stats(current_user)
