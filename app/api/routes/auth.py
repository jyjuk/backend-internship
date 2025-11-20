import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_auth_service
from app.services.auth import AuthService
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.schemas.user import UserDetail
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, service: AuthService = Depends(get_auth_service)):
    """Login with email and password"""
    return await service.login(data)


@router.get("/me", response_model=UserDetail)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user"""
    logger.info(f"User accessed /me endpoint: {current_user.email}")
    return UserDetail.model_validate(current_user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
        data: RefreshTokenRequest,
        service: AuthService = Depends(get_auth_service)
):
    """Refresh access token using refresh token"""
    return await service.refresh_access_token(data.refresh_token)
