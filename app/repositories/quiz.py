from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.quiz import Quiz
from app.repositories.base import BaseRepository


class QuizRepository(BaseRepository[Quiz]):
    """Repository for Quiz model"""

    def __init__(self, session: AsyncSession):
        super().__init__(Quiz, session)

    async def get_company_quizzes(self, company_id: UUID, skip: int = 0, limit: int = 100) -> List[Quiz]:
        """Get all quizzes for a company"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"company_id": company_id},
            order_by=Quiz.created_at.desc()
        )

    async def count_company_quizzes(self, company_id: UUID) -> int:
        """Count quizzes in company"""
        return await self.count(filters={"company_id": company_id})

    async def get_quiz_with_questions(self, quiz_id: UUID) -> Optional[Quiz]:
        """Get quiz with all questions and answers"""
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select

        stmt = select(Quiz).where(
            Quiz.id == quiz_id
        ).options(
            selectinload(
                Quiz.questions
            ).selectinload(
                Quiz.questions.property.mapper.class_.answers
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
