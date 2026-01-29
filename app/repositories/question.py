from sqlalchemy.ext.asyncio import AsyncSession
from app.models.question import Question
from app.repositories.base import BaseRepository
from uuid import UUID
from sqlalchemy import delete


class QuestionRepository(BaseRepository[Question]):
    """Repository for Question model"""

    def __init__(self, session: AsyncSession):
        super().__init__(Question, session)

    async def delete_by_quiz_id(self, quiz_id: UUID) -> None:
        """Delete all questions for a quiz (cascade deletes answers)"""
        await self.session.execute(
            delete(Question).where(Question.quiz_id == quiz_id)
        )
