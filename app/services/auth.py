import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, create_access_token
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def login(self, data: LoginRequest) -> TokenResponse:
        try:
            user = await self.repository.get_by_email(data.email)
            if not user:
                logger.warning(f"Login failed: user not found - {data.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            if not verify_password(data.password, user.hashed_password):
                logger.warning(f"Login failed: incorect password - {data.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            if not user.is_active:
                logger.warning(f"Login failed: inactive user - {data.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user"
                )

            access_token = create_access_token(data={"sub": user.email})

            logger.info(f"User logged in: {user.email}")
            return TokenResponse(access_token=access_token)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed"
            )
