import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.auth import AuthService
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserDetail
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email and password"""
    service = AuthService(db)
    return await service.login(data)


@router.get("/me", response_model=UserDetail)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user"""
    logger.info(f"User accessed /me endpoint: {current_user.email}")
    return UserDetail.model_validate(current_user)
