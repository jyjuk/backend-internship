from typing import Dict, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
import logging
from app.models.user import User
from app.models.quiz_attempt import QuizAttempt
from app.models.company_member import CompanyMember
from app.models.quiz import Quiz
from app.repositories.quiz_attempt import QuizAttemptRepository
from app.repositories.company import CompanyRepository
from app.repositories.company_member import CompanyMemberRepository
from app.repositories.quiz import QuizRepository
from app.schemas.analytics import (
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
    UserInCompanyAnalytics,
    WeeklyTrend
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics operations"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.attempt_repo = QuizAttemptRepository(session)
        self.company_repo = CompanyRepository(session)
        self.member_repo = CompanyMemberRepository(session)
        self.quiz_repo = QuizRepository(session)

    async def _check_owner_or_admin(self, company_id: UUID, user_id: UUID) -> None:
        """Check if user is company owner or admin"""
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
            trends.append(
                WeeklyTrend(
                    week=week,
                    avg_score=round(sum(scores) / len(scores), 2),
                    attempts=len(scores)
                )
            )
        return trends

    async def get_user_overall_analytics(self, user: User) -> UserOverallAnalytics:
        """Get user's overall analytics across all companies using SQL aggregation"""
        try:
            stats = await self.attempt_repo.get_user_overall_stats_sql(user.id)

            return UserOverallAnalytics(
                average_score=round(stats["average_score"], 2),
                total_attempts=stats["total_attempts"],
                total_companies=stats["total_companies"],
                total_quizzes_taken=stats["total_quizzes"]
            )
        except Exception as e:
            logger.error(f"Error getting user overall analytics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get analytics"
            )

    async def get_user_quiz_analytics(self, user: User) -> UserQuizAnalyticsList:
        """Get user's analytics for each quiz with trends using SQL aggregation"""
        try:
            quiz_stats = await self.attempt_repo.get_user_quiz_stats_sql(user.id)

            if not quiz_stats:
                return UserQuizAnalyticsList(quizzes=[])

            quiz_ids = [stat["quiz_id"] for stat in quiz_stats]
            stmt = select(QuizAttempt).where(
                QuizAttempt.user_id == user.id,
                QuizAttempt.quiz_id.in_(quiz_ids)
            ).options(
                selectinload(QuizAttempt.quiz),
                selectinload(QuizAttempt.company)
            )
            result = await self.session.execute(stmt)
            attempts = result.scalars().all()

            quiz_attempts: Dict[UUID, List[QuizAttempt]] = {}
            quiz_info: Dict[UUID, tuple] = {}
            for attempt in attempts:
                if attempt.quiz_id not in quiz_attempts:
                    quiz_attempts[attempt.quiz_id] = []
                    quiz_info[attempt.quiz_id] = (attempt.quiz, attempt.company)
                quiz_attempts[attempt.quiz_id].append(attempt)

            quiz_analytics = []
            for stat in quiz_stats:
                quiz_id = stat["quiz_id"]
                quiz, company = quiz_info[quiz_id]
                weekly_trend = await self._calculate_weekly_trends(quiz_attempts[quiz_id])
                quiz_analytics.append(
                    QuizAnalytics(
                        quiz_id=quiz_id,
                        quiz_title=quiz.title,
                        company_id=company.id,
                        company_name=company.name,
                        average_score=round(stat["average_score"], 2),
                        attempts_count=stat["attempts_count"],
                        last_attempt_at=stat["last_attempt_at"],
                        weekly_trend=weekly_trend
                        )
                )

            return UserQuizAnalyticsList(quizzes=quiz_analytics)
        except Exception as e:
            logger.error(f"Error getting user quiz analytics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get analytics"
            )

    async def get_user_recent_attempts(self, user: User, limit: int = 10) -> RecentAttemptsList:
        """Get user's recent quiz attempts"""
        try:
            stmt = select(QuizAttempt).where(
                QuizAttempt.user_id == user.id
            ).options(
                selectinload(QuizAttempt.quiz),
                selectinload(QuizAttempt.company)
            ).order_by(QuizAttempt.created_at.desc()).limit(limit)
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
            logger.error(f"Error getting user recent attempts: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get recent attempts"
            )

    async def get_company_overview_analytics(
            self,
            company_id: UUID,
            requester: User
    ) -> CompanyOverviewAnalytics:
        """Get company overview analytics with weekly trends using SQL aggregation"""
        try:
            await self._check_owner_or_admin(company_id, requester.id)
            company = await self.company_repo.get_by_id(company_id)
            stmt = select(func.count(CompanyMember.id)).where(
                CompanyMember.company_id == company_id
            )
            result = await self.session.execute(stmt)
            total_members = result.scalar() or 0
            stmt = select(func.count(Quiz.id)).where(Quiz.company_id == company_id)
            result = await self.session.execute(stmt)
            total_quizzes = result.scalar() or 0
            stats = await self.attempt_repo.get_company_overview_stats_sql(company_id)
            stmt = select(QuizAttempt).where(QuizAttempt.company_id == company_id)
            result = await self.session.execute(stmt)
            attempts = result.scalars().all()

            weekly_trend = await self._calculate_weekly_trends(attempts) if attempts else []

            return CompanyOverviewAnalytics(
                company_id=company_id,
                company_name=company.name,
                total_members=total_members,
                total_quizzes=total_quizzes,
                total_attempts=stats["total_attempts"],
                average_company_score=round(stats["average_score"], 2),
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

    async def get_company_members_analytics(
            self,
            company_id: UUID,
            requester: User
    ) -> CompanyMemberAnalyticsList:
        """Get analytics for all company members using SQL aggregation"""
        try:
            await self._check_owner_or_admin(company_id, requester.id)
            stmt = select(CompanyMember).where(
                CompanyMember.company_id == company_id
            ).options(selectinload(CompanyMember.user))
            result = await self.session.execute(stmt)
            members = result.scalars().all()
            members_stats = await self.attempt_repo.get_company_members_stats_sql(company_id)
            stats_dict = {stat["user_id"]: stat for stat in members_stats}

            member_analytics = []
            for member in members:
                stat = stats_dict.get(member.user_id, {
                    "total_attempts": 0,
                    "average_score": 0.0,
                    "last_attempt_at": None
                })
                member_analytics.append(
                    MemberAnalytics(
                        user_id=member.user_id,
                        username=member.user.username,
                        email=member.user.email,
                        total_attempts=stat["total_attempts"],
                        average_score=round(stat["average_score"], 2),
                        last_attempt_at=stat["last_attempt_at"]
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

    async def get_company_quizzes_analytics(
            self,
            company_id: UUID,
            requester: User
    ) -> CompanyQuizzesAnalytics:
        """Get analytics for all company quizzes with completion rates using SQL aggregation"""
        try:
            await self._check_owner_or_admin(company_id, requester.id)
            stmt = select(Quiz).where(Quiz.company_id == company_id)
            result = await self.session.execute(stmt)
            quizzes = result.scalars().all()
            stmt = select(
                func.count(CompanyMember.id)
            ).where(
                CompanyMember.company_id == company_id
            )
            result = await self.session.execute(stmt)
            total_members = result.scalar() or 1

            quizzes_stats = await self.attempt_repo.get_company_quizzes_stats_sql(company_id)
            stats_dict = {stat["quiz_id"]: stat for stat in quizzes_stats}
            stmt = select(QuizAttempt).where(QuizAttempt.company_id == company_id)
            result = await self.session.execute(stmt)
            all_attempts = result.scalars().all()
            quiz_attempts_map: Dict[UUID, List[QuizAttempt]] = {}
            for attempt in all_attempts:
                if attempt.quiz_id not in quiz_attempts_map:
                    quiz_attempts_map[attempt.quiz_id] = []
                quiz_attempts_map[attempt.quiz_id].append(attempt)
            quiz_analytics = []
            for quiz in quizzes:
                stat = stats_dict.get(
                    quiz.id,
                    {
                        "total_attempts": 0,
                        "average_score": 0.0,
                        "unique_users": 0
                    }
                )

                completion_rate = (stat["unique_users"] / total_members) * 100

                quiz_attempts_list = quiz_attempts_map.get(quiz.id, [])
                weekly_trend = await self._calculate_weekly_trends(quiz_attempts_list) if quiz_attempts_list else []

                quiz_analytics.append(
                    CompanyQuizAnalytics(
                        quiz_id=quiz.id,
                        quiz_title=quiz.title,
                        total_attempts=stat["total_attempts"],
                        average_score=round(stat["average_score"], 2),
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
        """Get detailed analytics for specific user in company using SQL aggregation"""
        try:
            await self._check_owner_or_admin(company_id, requester.id)
            member = await self.member_repo.get_by_user_and_company(user_id, company_id)
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User is not a member of this company"
                )
            company = await self.company_repo.get_by_id(company_id)

            stats = await self.attempt_repo.get_user_company_quiz_stats_sql(user_id, company_id)

            quiz_ids = [q["quiz_id"] for q in stats["quizzes"]]
            if quiz_ids:
                stmt = select(Quiz).where(Quiz.id.in_(quiz_ids))
                result = await self.session.execute(stmt)
                quizzes_list = result.scalars().all()
                quizzes_dict = {quiz.id: quiz for quiz in quizzes_list}

                stmt = select(QuizAttempt).where(
                    and_(
                        QuizAttempt.user_id == user_id,
                        QuizAttempt.company_id == company_id
                    )
                )
                result = await self.session.execute(stmt)
                attempts = result.scalars().all()

                quiz_attempts_map: Dict[UUID, List[QuizAttempt]] = {}
                for attempt in attempts:
                    if attempt.quiz_id not in quiz_attempts_map:
                        quiz_attempts_map[attempt.quiz_id] = []
                    quiz_attempts_map[attempt.quiz_id].append(attempt)

                quiz_analytics = []
                for quiz_stat in stats["quizzes"]:
                    quiz_id = quiz_stat["quiz_id"]
                    quiz = quizzes_dict.get(quiz_id)

                    if not quiz:
                        continue

                    quiz_attempts_list = quiz_attempts_map.get(quiz_id, [])
                    weekly_trend = await self._calculate_weekly_trends(quiz_attempts_list)

                    quiz_analytics.append(
                        QuizAnalytics(
                            quiz_id=quiz_id,
                            quiz_title=quiz.title,
                            company_id=company_id,
                            company_name=company.name,
                            average_score=round(quiz_stat["average_score"], 2),
                            attempts_count=quiz_stat["attempts_count"],
                            last_attempt_at=quiz_stat["last_attempt_at"],
                            weekly_trend=weekly_trend
                        )
                    )
            else:
                quiz_analytics = []
            return UserInCompanyAnalytics(
                user_id=user_id,
                username=member.user.username,
                company_id=company_id,
                company_name=company.name,
                total_attempts=stats["total_attempts"],
                average_score=round(stats["average_score"], 2),
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
