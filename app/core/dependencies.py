import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.auth0 import verify_auth0_token
from app.repositories.user import UserRepository
from app.models.user import User

security = HTTPBearer()
logger = logging.getLogger(__name__)


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user"""
    token = credentials.credentials
    payload = verify_auth0_token(token)

    if payload is None:
        payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    email: Optional[str] = payload.get("email") or payload.get("sub")

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    repository = UserRepository(db)
    user = await repository.get_by_email(email)

    if user is None and payload.get("email"):
        from app.models.user import User as UserModel
        from app.core.security import hash_password
        import secrets

        user = UserModel(
            email=payload["email"],
            username=payload.get("nickname", payload["email"].split("@")[0]),
            hashed_password=hash_password(secrets.token_urlsafe(32)),
            is_active=True
        )
        user = await repository.create(user)
        logger.info(f"Created new user from Auth0: {user.email}")
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user


def get_auth_service(db: AsyncSession = Depends(get_db)):
    """Get authservice instance"""
    from app.services.auth import AuthService
    return AuthService(db)
