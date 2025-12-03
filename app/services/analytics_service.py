import logging
from uuid import UUID
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy import func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz import Quiz
from app.models.company import Company
from app.repositories.company import CompanyRepository
from app.repositories.company_member import CompanyMemberRepository
from app.repositories.quiz_attempt import QuizAttemptRepository
from app.schemas.analytics import (
    WeeklyTrend,
    UserOverallAnalytics,
    QuizAnalytics,
    UserQuizAnalyticsList,
    RecentAttempt,
    RecentAttemptsList,
    CompanyOverviewAnalytics,
    MemberAnalytics,
    CompanyMemberAnalyticsList,
    CompanyQuizAnalytics,
    CompanyQuizzesAnalytics,
    UserInCompanyAnalytics
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and statistics"""

    def __init__(self, session: AsyncSession):
        self.company_repo = CompanyRepository(session)
        self.member_repo = CompanyMemberRepository(session)
        self.attempt_repo = QuizAttemptRepository(session)
        self.session = session

    async def _check_owner_or_admin(self, company_id: UUID, user_id: UUID) -> None:
        """Check id user is company owner or admin"""
        company = await self.company_repo.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        if company.owner_id == user_id:
            return
        member = await self.member_repo.get_by_user_and_company(user_id, company_id)
        if not member or not member.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only company owner or admin can access this analytics"
            )

    @staticmethod
    def _get_week_number(date: datetime) -> str:
        """Get ISO week number in format: 2024-W48"""
        return f"{date.year}-W{date.isocalendar()[1]:02d}"

    async def _calculate_weekly_trends(self, attempts: List[QuizAttempt]) -> List[WeeklyTrend]:
        """Calculate weekly trends from attempts"""
        if not attempts:
            return []

        weekly_data: Dict[str, List[float]] = {}
        for attempt in attempts:
            week = self._get_week_number(attempt.created_at)
            percentage = (attempt.score / attempt.total_questions) * 100

            if week not in weekly_data:
                weekly_data[week] = []
            weekly_data[week].append(percentage)

        trends = []
        for week in sorted(weekly_data.keys()):
            scores = weekly_data[week]
            trends.append(WeeklyTrend(week=week, avg_score=round(sum(scores) / len(scores), 2), attempts=len(scores)))
        return trends

    async def get_user_overall_analytics(self, user: User) -> UserOverallAnalytics:
        """Get user`s overall analytics across all companies"""
        try:
            attempts = await self.attempt_repo.get_user_attempts(user.id)
            if not attempts:
                return UserOverallAnalytics(average_score=0, total_attempts=0, total_companies=0, total_quizzes_taken=0)

            total_score = sum((a.score / a.total_questions) * 100 for a in attempts)
            average_score = total_score / len(attempts)

            unique_companies = len(set(a.company_id for a in attempts))
            unique_quizzes = len(set(a.quiz_id for a in attempts))

            return UserOverallAnalytics(
                average_score=round(average_score, 2),
                total_attempts=len(attempts),
                total_companies=unique_companies,
                total_quizzes=unique_quizzes
            )
        except Exception as e:
            logger.error(f"Error getting user overall analytics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get analytics"
            )

    async def get_user_quiz_analytics(self, user: User) -> UserQuizAnalyticsList:
        """Get user`s analytics for each quiz with trends"""
        try:
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload

            stmt = select(
                QuizAttempt
            ).where(
                QuizAttempt.user_id == user.id
            ).options(
                selectinload(QuizAttempt.quiz),
                selectinload(QuizAttempt.company)
            )
            result = await self.session.execute(stmt)
            attempts = result.scalars().all()

            if not attempts:
                return UserQuizAnalyticsList(quizzes=[])
            quiz_attempts: Dict[UUID, List[QuizAttempt]] = {}
            for attempt in attempts:
                if attempt.quiz_id not in quiz_attempts:
                    quiz_attempts[attempt.quiz_id] = []
                quiz_attempts[attempt.quiz_id].append(attempt)

            quiz_analytics = []
            for quiz_id, quiz_attempts_list in quiz_attempts.items():
                first_attempt = quiz_attempts_list[0]
                total_score = sum((a.score / a.total_questions) * 100 for a in quiz_attempts_list)
                avg_score = total_score / len(quiz_attempts_list)
                weekly_trend = await self._calculate_weekly_trends(quiz_attempts_list)
                last_attempt = max(quiz_attempts_list, key=lambda a: a.created_at)
                quiz_analytics.append(QuizAnalytics(
                    quiz_id=quiz_id,
                    quiz_title=first_attempt.quiz.title,
                    company_id=first_attempt.company_id,
                    company_name=first_attempt.company.name,
                    average_score=round(avg_score, 2),
                    attempts_count=len(quiz_attempts_list),
                    last_attempt_at=last_attempt.created_at,
                    weekly_trend=weekly_trend
                ))
            return UserQuizAnalyticsList(quizzes=quiz_analytics)
        except Exception as e:
            logger.error(f"Error getting user quiz analytics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get quiz analytics"
            )

    async def get_user_recent_attempts(self, user: User, limit: int = 10) -> RecentAttemptsList:
        """Get user`s recent quiz attempts"""
        try:
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload

            stmt = select(
                QuizAttempt
            ).where(
                QuizAttempt.user_id == user.id
            ).options(
                selectinload(QuizAttempt.quiz),
                selectinload(QuizAttempt.company)
            ).order_by(
                QuizAttempt.created_at.desc()
            ).limit(limit)
            result = await self.session.execute(stmt)
            attempts = result.scalars().all()
            recent_attempts = [
                RecentAttempt(
                    quiz_id=attempt.quiz_id,
                    quiz_title=attempt.quiz.title,
                    company_name=attempt.company.name,
                    score=attempt.score,
                    total_questions=attempt.total_questions,
                    percentage=round((attempt.score / attempt.total_questions) * 100, 2),
                    completed_at=attempt.created_at
                )
                for attempt in attempts
            ]
            return RecentAttemptsList(attempts=recent_attempts)
        except Exception as e:
            logger.error(f"Error getting recent attempts: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get recent attempts"
            )

    async def get_company_overview_analytics(self, company_id: UUID, requester: User) -> CompanyOverviewAnalytics:
        """Get company overview analytics"""
        try:
            await self._check_owner_or_admin(company_id, requester.id)
            company = await self.company_repo.get_by_id(company_id)
            from sqlalchemy import select, func
            from app.models.company_member import CompanyMember

            stmt = select(func.count(CompanyMember.id)).where(CompanyMember.company_id == company_id)
            result = await self.session.execute(stmt)
            total_members = result.scalar() or 0
            stmt = select(func.count(Quiz.id)).where(Quiz.company_id == company_id)
            result = await self.session.execute(stmt)
            total_quizzes = result.scalar() or 0
            stmt = select(QuizAttempt).where(QuizAttempt.company_id == company_id)
            result = await self.session.execute(stmt)
            attempts = result.scalars().all()

            total_attempts = len(attempts)

            if attempts:
                total_score = sum((a.score / a.total_questions) * 100 for a in attempts)
                average_company_score = total_score / len(attempts)
                weekly_trend = await self._calculate_weekly_trends(attempts)
            else:
                average_company_score = 0.0
                weekly_trend = []

            return CompanyOverviewAnalytics(
                company_id=company_id,
                company_name=company.name,
                total_members=total_members,
                total_quizzes=total_quizzes,
                total_attempts=total_attempts,
                average_company_score=round(average_company_score, 2),
                weekly_trend=weekly_trend
            )
        except HTTPException:
            raise

        except Exception as e:
            logger.error(f"Error getting company overview analytics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get company analytics"
            )

    async def get_company_members_analytics(self, company_id: UUID, requester: User) -> CompanyMemberAnalyticsList:
        """Get analytics for all company members (owner/admin only)"""
        try:
            await self._check_owner_or_admin(company_id, requester.id)
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload
            from app.models.company_member import CompanyMember

            stmt = select(
                CompanyMember
            ).where(
                CompanyMember.company_id == company_id
            ).options(
                selectinload(CompanyMember.user)
            )
            result = await self.session.execute(stmt)
            members = result.scalars().all()

            member_analytics = []
            for member in members:
                user_attempts = await self.attempt_repo.get_user_company_attempts(
                    member.user_id,
                    company_id
                )

                if user_attempts:
                    total_score = sum((a.score / a.total_questions) * 100 for a in user_attempts)
                    avg_score = total_score / len(user_attempts)
                    last_attempt = max(user_attempts, key=lambda a: a.created_at)
                    last_attempt_at = last_attempt.created_at
                else:
                    avg_score = 0.0
                    last_attempt_at = None

                member_analytics.append(
                    MemberAnalytics(
                        user_id=member.user_id,
                        username=member.user.username,
                        email=member.user.email,
                        total_attempts=len(user_attempts),
                        average_score=round(avg_score, 2),
                        last_attempt_at=last_attempt_at
                    )
                )
            return CompanyMemberAnalyticsList(members=member_analytics)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting company members analytics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get members analytics"
            )

    async def get_company_quizzes_analytics(self, company_id: UUID, requester: User) -> CompanyQuizzesAnalytics:
        """Get analytics for all company quizzes (owner/admin only)"""
        try:
            await self._check_owner_or_admin(company_id, requester.id)
            from sqlalchemy import select
            stmt = select(Quiz).where(Quiz.company_id == company_id)
            result = await self.session.execute(stmt)
            quizzes = result.scalars().all()
            from app.models.company_member import CompanyMember
            stmt = select(
                func.count(
                    CompanyMember.id)
            ).where(
                CompanyMember.company_id == company_id
            )
            result = await self.session.execute(stmt)
            total_members = result.scalar() or 1

            quiz_analytics = []
            for quiz in quizzes:
                stmt = select(QuizAttempt).where(QuizAttempt.quiz_id == quiz.id)
                result = await self.session.execute(stmt)
                attempts = result.scalars().all()

                if attempts:
                    total_score = sum((a.score / a.total_questions) * 100 for a in attempts)
                    avg_score = total_score / len(attempts)
                    unique_users = len(set(a.user_id for a in attempts))
                    completion_rate = (unique_users / total_members) * 100
                    weekly_trend = await self._calculate_weekly_trends(attempts)
                else:
                    avg_score = 0.0
                    completion_rate = 0.0
                    weekly_trend = []

                quiz_analytics.append(
                    CompanyQuizAnalytics(
                        quiz_id=quiz.id,
                        quiz_title=quiz.title,
                        total_attempts=len(attempts),
                        average_score=round(avg_score, 2),
                        completion_rate=round(completion_rate, 2),
                        weekly_trend=weekly_trend
                    )
                )
            return CompanyQuizzesAnalytics(quizzes=quiz_analytics)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting company quizzes analytics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get quizzes analytics"
            )

    async def get_user_in_company_analytics(
            self,
            company_id: UUID,
            user_id: UUID,
            requester: User
    ) -> UserInCompanyAnalytics:
        """Get detailed analytics for specific user in company (owner/admin only)"""
        try:
            await self._check_owner_or_admin(company_id, requester.id)
            member = await self.member_repo.get_by_user_and_company(user_id, company_id)
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User is not a member of this company"
                )
            company = await self.company_repo.get_by_id(company_id)

            from sqlalchemy import select
            from sqlalchemy.orm import selectinload

            stmt = select(
                QuizAttempt
            ).where(
                and_(
                    QuizAttempt.user_id == user_id,
                    QuizAttempt.company_id == company_id
                )
            ).options(
                selectinload(
                    QuizAttempt.quiz
                )
            )
            result = await self.session.execute(stmt)
            attempts = result.scalars().all()

            if attempts:
                total_score = sum((a.score / a.total_questions) * 100 for a in attempts)
                avg_score = total_score / len(attempts)
            else:
                avg_score = 0.0

            quiz_attempts: Dict[UUID, List[QuizAttempt]] = {}
            for attempt in attempts:
                if attempt.quiz_id not in quiz_attempts:
                    quiz_attempts[attempt.quiz_id] = []
                quiz_attempts[attempt.quiz_id].append(attempt)

            quiz_analytics = []
            for quiz_id, quiz_attempts_list in quiz_attempts.items():
                first_attempt = quiz_attempts_list[0]
                total_score = sum((a.score / a.total_questions) * 100 for a in quiz_attempts_list)
                quiz_avg = total_score / len(quiz_attempts_list)
                weekly_trend = await self._calculate_weekly_trends(quiz_attempts_list)
                last_attempt = max(quiz_attempts_list, key=lambda a: a.created_at)
                quiz_analytics.append(
                    QuizAnalytics(
                        quiz_id=quiz_id,
                        quiz_title=first_attempt.quiz.title,
                        company_id=company_id,
                        company_name=company.name,
                        average_score=round(quiz_avg, 2),
                        attempts_count=len(quiz_attempts_list),
                        last_attempt_at=last_attempt.created_at,
                        weekly_trend=weekly_trend
                    )
                )
            return UserInCompanyAnalytics(
                user_id=user_id,
                username=member.user.username,
                company_id=company_id,
                company_name=company.name,
                total_attempts=len(attempts),
                average_score=round(avg_score, 2),
                quizzes=quiz_analytics
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user in company analytics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user analytics"
            )
