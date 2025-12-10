from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.scheduled_quiz_reminder import ScheduledQuizReminderService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])


@router.post("/trigger-quiz-reminder")
async def trigger_quiz_reminder_manually(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger quiz reminder check (for testing)
    Only for development/testing purposes
    """
    logger.info(f"Manual trigger by user {current_user.username}")

    service = ScheduledQuizReminderService(db)
    stats = await service.check_and_notify_pending_quizzes()

    return {
        "message": "Quiz reminder check completed",
        "stats": stats
    }
