from sqlalchemy.ext.asyncio import AsyncSession
from app.models.question import Question
from app.repositories.base import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    """Repository for Question model"""
    def __init__(self, session: AsyncSession):
        super().__init__(Question, session)
