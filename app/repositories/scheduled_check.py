from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.company_member import CompanyMember
from app.models.user import User
from app.models.company import Company
import logging

logger = logging.getLogger(__name__)


class ScheduledCheckRepository:
    """Repository for scheduled quiz completion checks"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active_users(self) -> List[User]:
        """Get all active users"""
        query = select(User).where(User.is_active == True)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_available_quizzes(self, user_id: UUID) -> List[Quiz]:
        """
        Get all quizzes available to user through company memberships
        User can access quizzes from companies they are member of
        """
        query = (
            select(Quiz)
            .join(CompanyMember, CompanyMember.company_id == Quiz.company_id)
            .where(CompanyMember.user_id == user_id)
            .distinct()
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_last_quiz_attempt_time(
            self,
            user_id: UUID,
            quiz_id: UUID
    ) -> Optional[datetime]:
        """Get timestamp of user's last attempt for specific quiz"""
        query = (
            select(func.max(QuizAttempt.completed_at))
            .where(
                QuizAttempt.user_id == user_id,
                QuizAttempt.quiz_id == quiz_id
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_company_name(self, company_id: UUID) -> str:
        """Get company name by id"""
        query = select(Company.name).where(Company.id == company_id)
        result = await self.session.execute(query)
        name = result.scalar_one_or_none()
        return name or "Unknown Company"

    async def get_users_pending_quizzes(self) -> List[Dict]:
        """
        Get all users with quizzes they haven't completed in last 24 hours

        Returns list of dicts with structure:
        {
            "user_id": UUID,
            "user_email": str,
            "user_username": str,
            "quiz_id": UUID,
            "quiz_title": str,
            "company_id": UUID,
            "company_name": str,
            "last_attempt": datetime or None
        }
        """
        pending = []

        users = await self.get_all_active_users()
        logger.info(f"Checking {len(users)} active users for pending quizzes")

        time_threshold = datetime.now(timezone.utc) - timedelta(hours=24)

        for user in users:
            quizzes = await self.get_user_available_quizzes(user.id)

            for quiz in quizzes:
                last_attempt = await self.get_last_quiz_attempt_time(
                    user.id,
                    quiz.id
                )

                needs_reminder = (
                        last_attempt is None or
                        last_attempt < time_threshold
                )

                if needs_reminder:
                    company_name = await self.get_company_name(quiz.company_id)

                    pending.append({
                        "user_id": user.id,
                        "user_email": user.email,
                        "user_username": user.username,
                        "quiz_id": quiz.id,
                        "quiz_title": quiz.title,
                        "company_id": quiz.company_id,
                        "company_name": company_name,
                        "last_attempt": last_attempt
                    })

        logger.info(f"Found {len(pending)} pending quiz reminders")
        return pending
