from fastapi import APIRouter, Depends, status, Query
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.quiz_service import QuizService
from app.schemas.quiz import QuizCreate, QuizUpdate, QuizResponse, QuizList
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.quiz_attempt_service import QuizAttemptService
from app.schemas.quiz import QuizSubmission, QuizAttemptResponse, UserCompanyStats, UserSystemStats

router = APIRouter(prefix="/companies", tags=["Quizzes"])


@router.post("/{company_id}/quizzes", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
        company_id: UUID,
        quiz_data: QuizCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Create a new quiz - owner or admin only"""
    service = QuizService(db)
    return await service.create_quiz(company_id, quiz_data, current_user)


@router.get("/{company_id}/quizzes", response_model=QuizList)
async def get_company_quizzes(
        company_id: UUID,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    """Get all quizzes for a company"""
    service = QuizService(db)
    return await service.get_company_quizzes(company_id, skip, limit)


@router.get("/{company_id}/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
        company_id: UUID,
        quiz_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    """Get quiz details"""
    service = QuizService(db)
    return await service.get_quiz(company_id, quiz_id)


@router.put("/{company_id}/quizzes/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
        company_id: UUID,
        quiz_id: UUID,
        quiz_data: QuizUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Update quiz - owner or admin only"""
    service = QuizService(db)
    return await service.update_quiz(company_id, quiz_id, quiz_data, current_user)


@router.delete("/{company_id}/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
        company_id: UUID,
        quiz_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Delete quiz - owner or admin only"""
    service = QuizService(db)
    await service.delete_quiz(company_id, quiz_id, current_user)


@router.post("/{company_id}/quizzes/{quiz_id}/attempts", response_model=QuizAttemptResponse)
async def submit_quiz(
        company_id: UUID,
        quiz_id: UUID,
        submission: QuizSubmission,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Submit quiz answers and get results"""
    service = QuizAttemptService(db)
    return await service.submit_quiz(company_id, quiz_id, submission, current_user)


@router.get("/{company_id}/my-stats", response_model=UserCompanyStats)
async def get_my_company_stats(
        company_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get my quiz statistics in this company"""
    service = QuizAttemptService(db)
    return await service.get_user_company_stats(company_id, current_user)
