import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from app.core.database import AsyncSessionLocal
from app.services.scheduled_quiz_reminder import ScheduledQuizReminderService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def scheduled_quiz_reminder_job():
    """
    Scheduled job that runs every 24 hours at midnight
    Checks all users and sends quiz reminder notifications
    """
    logger.info("Running scheduled quiz reminder job")

    async with AsyncSessionLocal() as session:
        try:
            service = ScheduledQuizReminderService(session)

            stats = await service.check_and_notify_pending_quizzes()

            logger.info(
                f"Scheduled job completed: "
                f"{stats['users_checked']} users, "
                f"{stats['pending_quizzes']} pending quizzes, "
                f"{stats['notifications_sent']} notifications sent, "
                f"{stats['errors']} errors"
            )

        except Exception as e:
            logger.error(f"Error in scheduled job: {str(e)}")

        finally:
            await session.close()


def start_scheduler():
    """Start the APScheduler"""
    scheduler.add_job(
        scheduled_quiz_reminder_job,
        trigger=CronTrigger(hour=0, minute=0),
        id="quiz_reminder_job",
        name="Daily Quiz Reminder Check",
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started: Quiz reminder job scheduled for daily at midnight")


def shutdown_scheduler():
    """Shutdown the scheduler gracefully"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down")
