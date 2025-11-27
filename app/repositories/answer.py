from sqlalchemy.ext.asyncio import AsyncSession
from app.models.answer import Answer
from app.repositories.base import BaseRepository


class AnswerRepository(BaseRepository[Answer]):
    """Repository for Answer model"""

    def __init__(self, session: AsyncSession):
        super().__init__(Answer, session)
