from fastapi import APIRouter, Depends, Query
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    UserQuizAnalyticsList,
    UserOverallAnalytics,
    UserInCompanyAnalytics,
    CompanyOverviewAnalytics,
    CompanyMemberAnalyticsList,
    CompanyQuizzesAnalytics,
    RecentAttemptsList
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/users/me/overall", response_model=UserOverallAnalytics)
async def get_my_overall_analytics(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get my overall analytics across all companies"""
    service = AnalyticsService(db)
    return await service.get_user_overall_analytics(current_user)


@router.get("/users/me/quizzes", response_model=UserQuizAnalyticsList)
async def get_my_quiz_analytics(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get my analytics for each quiz with weekly trends"""
    service = AnalyticsService(db)
    return await service.get_user_quiz_analytics(current_user)


@router.get("/users/me/recent-attempts", response_model=RecentAttemptsList)
async def get_my_recent_attempts(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        limit: int = Query(10, ge=1, le=50, description="Number of recent attempts")
):
    """Get my recent quiz attempts"""
    service = AnalyticsService(db)
    return await service.get_user_recent_attempts(current_user, limit=limit)


@router.get("/companies/{company_id}/overview", response_model=CompanyOverviewAnalytics)
async def get_company_overview_analytics(
        company_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get company overview analytics with weekly trends"""
    service = AnalyticsService(db)
    return await service.get_company_overview_analytics(company_id, current_user)


@router.get("/companies/{company_id}/members", response_model=CompanyMemberAnalyticsList)
async def get_company_members_analytics(
        company_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """Get analytics for all company members"""
    service = AnalyticsService(db)
    return await service.get_company_members_analytics(company_id, current_user)


@router.get("/companies/{company_id}/quizzes", response_model=CompanyQuizzesAnalytics)
async def get_company_quizzes_analytics(
        company_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """Get analytics for all company quiz with completion rates"""
    service = AnalyticsService(db)
    return await service.get_company_quizzes_analytics(company_id, current_user)


@router.get("/companies/{company_id}/users/{user_id}", response_model=UserInCompanyAnalytics)
async def get_user_in_company_analytics(
        user_id: UUID,
        company_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """Get detailed analytics for specific user in company"""
    service = AnalyticsService(db)
    return await service.get_user_in_company_analytics(company_id, user_id, current_user)
