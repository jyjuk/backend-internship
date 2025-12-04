from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.quiz_attempt import QuizAttempt
from app.repositories.base import BaseRepository


class QuizAttemptRepository(BaseRepository[QuizAttempt]):
    """Repository for QuizAttempt model"""

    def __init__(self, session: AsyncSession):
        super().__init__(QuizAttempt, session)

    async def get_user_attempts(
            self,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> List[QuizAttempt]:
        """Get all attempts for a user"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"user_id": user_id},
            order_by=QuizAttempt.created_at.desc()
        )

    async def get_user_company_attempts(
            self,
            user_id: UUID,
            company_id: UUID
    ) -> List[QuizAttempt]:
        """Get all attempts for a user in a specific company"""
        return await self.get_all(
            filters={"user_id": user_id, "company_id": company_id},
            order_by=QuizAttempt.created_at.desc()
        )

    async def get_last_attempt(
            self,
            user_id: UUID,
            quiz_id: UUID
    ) -> Optional[QuizAttempt]:
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

    async def get_by_company(self, company_id: UUID) -> List[QuizAttempt]:
        """Get all attempts for a company"""
        return await self.get_all(
            filters={"company_id": company_id},
            order_by=QuizAttempt.created_at.desc()
        )

    async def get_user_quiz_attempts_with_relations(
            self,
            user_id: UUID,
            quiz_ids: List[UUID]
    ) -> List[QuizAttempt]:
        """Get user attempts for specific quizzes with quiz and company relations loaded"""
        stmt = select(
            QuizAttempt
        ).where(
            QuizAttempt.user_id == user_id,
            QuizAttempt.quiz_id.in_(quiz_ids)
        ).options(
            selectinload(QuizAttempt.quiz),
            selectinload(QuizAttempt.company)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_recent_attempts_with_relations(
            self,
            user_id: UUID,
            limit: int = 10
    ) -> List[QuizAttempt]:
        """Get user's recent attempts with quiz and company relations loaded"""
        stmt = select(
            QuizAttempt
        ).where(
            QuizAttempt.user_id == user_id
        ).options(
            selectinload(QuizAttempt.quiz),
            selectinload(QuizAttempt.company)
        ).order_by(
            QuizAttempt.created_at.desc()
        ).limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_user_and_company_with_relations(
            self,
            user_id: UUID,
            company_id: UUID
    ) -> List[QuizAttempt]:
        """Get user attempts in company with quiz relations loaded"""
        stmt = select(
            QuizAttempt
        ).where(
            and_(
                QuizAttempt.user_id == user_id,
                QuizAttempt.company_id == company_id
            )
        ).options(
            selectinload(QuizAttempt.quiz)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_overall_stats_sql(self, user_id: UUID) -> dict:
        """Get user overall statistics using SQL aggregation"""
        stmt = select(
            func.count(QuizAttempt.id).label("total_attempts"),
            func.count(func.distinct(QuizAttempt.company_id)).label("total_companies"),
            func.count(func.distinct(QuizAttempt.quiz_id)).label("total_quizzes"),
            func.avg(
                (QuizAttempt.score * 100.0) / QuizAttempt.total_questions
            ).label("average_score")
        ).where(QuizAttempt.user_id == user_id)

        result = await self.session.execute(stmt)
        row = result.one()

        return {
            "total_attempts": row.total_attempts or 0,
            "total_companies": row.total_companies or 0,
            "total_quizzes": row.total_quizzes or 0,
            "average_score": float(row.average_score) if row.average_score else 0.0
        }

    async def get_user_quiz_stats_sql(self, user_id: UUID) -> list[dict]:
        """Get user statistics per quiz using SQL aggregation"""
        stmt = select(
            QuizAttempt.quiz_id,
            func.count(QuizAttempt.id).label("attempts_count"),
            func.avg(
                (QuizAttempt.score * 100.0) / QuizAttempt.total_questions
            ).label("average_score"),
            func.max(QuizAttempt.created_at).label("last_attempt_at")
        ).where(
            QuizAttempt.user_id == user_id
        ).group_by(
            QuizAttempt.quiz_id
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                "quiz_id": row.quiz_id,
                "attempts_count": row.attempts_count,
                "average_score": float(row.average_score) if row.average_score else 0.0,
                "last_attempt_at": row.last_attempt_at
            }
            for row in rows
        ]

    async def get_company_overview_stats_sql(self, company_id: UUID) -> dict:
        """Get company overview statistics using SQL aggregation"""
        stmt = select(
            func.count(QuizAttempt.id).label("total_attempts"),
            func.avg(
                (QuizAttempt.score * 100.0) / QuizAttempt.total_questions
            ).label("average_score")
        ).where(QuizAttempt.company_id == company_id)

        result = await self.session.execute(stmt)
        row = result.one()

        return {
            "total_attempts": row.total_attempts or 0,
            "average_score": float(row.average_score) if row.average_score else 0.0
        }

    async def get_company_members_stats_sql(self, company_id: UUID) -> list[dict]:
        """Get statistics for all company members using SQL aggregation"""
        stmt = select(
            QuizAttempt.user_id,
            func.count(QuizAttempt.id).label("total_attempts"),
            func.avg(
                (QuizAttempt.score * 100.0) / QuizAttempt.total_questions
            ).label("average_score"),
            func.max(QuizAttempt.created_at).label("last_attempt_at")
        ).where(
            QuizAttempt.company_id == company_id
        ).group_by(
            QuizAttempt.user_id
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                "user_id": row.user_id,
                "total_attempts": row.total_attempts,
                "average_score": float(row.average_score) if row.average_score else 0.0,
                "last_attempt_at": row.last_attempt_at
            }
            for row in rows
        ]

    async def get_company_quizzes_stats_sql(self, company_id: UUID) -> list[dict]:
        """Get statistics for all company quizzes using SQL aggregation"""
        stmt = select(
            QuizAttempt.quiz_id,
            func.count(QuizAttempt.id).label("total_attempts"),
            func.avg(
                (QuizAttempt.score * 100.0) / QuizAttempt.total_questions
            ).label("average_score"),
            func.count(func.distinct(QuizAttempt.user_id)).label("unique_users")
        ).where(
            QuizAttempt.company_id == company_id
        ).group_by(
            QuizAttempt.quiz_id
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                "quiz_id": row.quiz_id,
                "total_attempts": row.total_attempts,
                "average_score": float(row.average_score) if row.average_score else 0.0,
                "unique_users": row.unique_users
            }
            for row in rows
        ]

    async def get_user_company_quiz_stats_sql(self, user_id: UUID, company_id: UUID) -> dict:
        """Get user statistics in specific company using SQL aggregation"""
        overall_stmt = select(
            func.count(QuizAttempt.id).label("total_attempts"),
            func.avg(
                (QuizAttempt.score * 100.0) / QuizAttempt.total_questions
            ).label("average_score")
        ).where(
            QuizAttempt.user_id == user_id,
            QuizAttempt.company_id == company_id
        )

        result = await self.session.execute(overall_stmt)
        overall = result.one()

        quiz_stmt = select(
            QuizAttempt.quiz_id,
            func.count(QuizAttempt.id).label("attempts_count"),
            func.avg(
                (QuizAttempt.score * 100.0) / QuizAttempt.total_questions
            ).label("average_score"),
            func.max(QuizAttempt.created_at).label("last_attempt_at")
        ).where(
            QuizAttempt.user_id == user_id,
            QuizAttempt.company_id == company_id
        ).group_by(
            QuizAttempt.quiz_id
        )

        result = await self.session.execute(quiz_stmt)
        quiz_rows = result.all()

        return {
            "total_attempts": overall.total_attempts or 0,
            "average_score": float(overall.average_score) if overall.average_score else 0.0,
            "quizzes": [
                {
                    "quiz_id": row.quiz_id,
                    "attempts_count": row.attempts_count,
                    "average_score": float(row.average_score) if row.average_score else 0.0,
                    "last_attempt_at": row.last_attempt_at
                }
                for row in quiz_rows
            ]
        }
