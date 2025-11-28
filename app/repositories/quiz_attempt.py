from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.quiz_attempt import QuizAttempt
from app.repositories.base import BaseRepository


class QuizAttemptRepository(BaseRepository[QuizAttempt]):
    """Repository for QuizAttempt model"""

    def __init__(self, session: AsyncSession):
        super().__init__(QuizAttempt, session)

    async def get_user_attempts(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[QuizAttempt]:
        """Get all attempts for a user"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"user_id": user_id},
            order_by=QuizAttempt.created_at.desc()
        )

    async def get_user_company_attempts(self, user_id: UUID, company_id: UUID) -> List[QuizAttempt]:
        """Get all attempts for a user in a specific company"""
        return await self.get_all(
            filters={"user_id": user_id, "company_id": company_id},
            order_by=QuizAttempt.created_at.desc()
        )

    async def get_last_attempt(self, user_id: UUID, quiz_id: UUID) -> Optional[QuizAttempt]:
        """Get user`s last attempt for a specific quiz"""
        result = await self.get_all(
            limit=1,
            filters={"user_id": user_id, "quiz_id": quiz_id},
            order_by=QuizAttempt.created_at.desc()
        )
        return result[0] if result else None

    async def get_user_company_stats(self, user_id: UUID, company_id: UUID) -> dict:
        """Get user statistics within a company"""
        stmt = select(
            func.count(QuizAttempt.id).label("total_attempts"),
            func.sum(QuizAttempt.total_questions).label("total_questions"),
            func.sum(QuizAttempt.score).label("total_correct"),
            func.max(QuizAttempt.created_at).label("last_attempt")
        ).where(
            QuizAttempt.user_id == user_id,
            QuizAttempt.company_id == company_id
        )
        result = await self.session.execute(stmt)
        row = result.first()
        return {
            "total_attempts": row.total_attempts or 0,
            "total_questions": row.total_questions or 0,
            "total_correct": row.total_correct or 0,
            "last_attempt": row.last_attempt
        }

    async def get_user_system_stats(self, user_id: UUID) -> dict:
        """Get user statistics across all companies"""
        stmt = select(
            func.count(QuizAttempt.id).label("total_attempts"),
            func.sum(QuizAttempt.total_questions).label("total_questions"),
            func.sum(QuizAttempt.score).label("total_correct"),
            func.max(QuizAttempt.created_at).label("last_attempt"),
            func.count(func.distinct(QuizAttempt.company_id)).label("companies_count")
        ).where(QuizAttempt.user_id == user_id)
        result = await self.session.execute(stmt)
        row = result.first()

        return {
            "total_attempts": row.total_attempts or 0,
            "total_questions": row.total_questions or 0,
            "total_correct": row.total_correct or 0,
            "last_attempt": row.last_attempt,
            "companies_count": row.companies_count or 0
        }
