import logging
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.scheduled_check import ScheduledCheckRepository
from app.repositories.notification import NotificationRepository
from app.core.websocket import manager

logger = logging.getLogger(__name__)


class ScheduledQuizReminderService:
    """Service for scheduled quiz reminder notifications"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.scheduled_repo = ScheduledCheckRepository(session)
        self.notification_repo = NotificationRepository(session)

    async def check_and_notify_pending_quizzes(self) -> Dict[str, int]:
        """
        Main scheduled task: check all users and send reminders

        Returns:
            dict with stats: {
                "users_checked": int,
                "pending_quizzes": int,
                "notifications_sent": int,
                "errors": int
            }
        """
        stats = {
            "users_checked": 0,
            "pending_quizzes": 0,
            "notifications_sent": 0,
            "errors": 0
        }

        try:
            logger.info("Starting scheduled quiz reminder check")

            pending_quizzes = await self.scheduled_repo.get_users_pending_quizzes()

            stats["pending_quizzes"] = len(pending_quizzes)

            unique_users = set(pq["user_id"] for pq in pending_quizzes)
            stats["users_checked"] = len(unique_users)

            logger.info(
                f"Found {stats['pending_quizzes']} pending quizzes "
                f"for {stats['users_checked']} users"
            )

            for pending in pending_quizzes:
                try:
                    await self._send_reminder_notification(pending)
                    stats["notifications_sent"] += 1

                except Exception as e:
                    logger.error(
                        f"Error sending reminder for user {pending['user_id']} "
                        f"quiz {pending['quiz_id']}: {str(e)}"
                    )
                    stats["errors"] += 1

            logger.info(
                f"Scheduled check completed. "
                f"Sent {stats['notifications_sent']} notifications, "
                f"{stats['errors']} errors"
            )

            return stats

        except Exception as e:
            logger.error(f"Error in scheduled quiz reminder check: {str(e)}")
            stats["errors"] += 1
            return stats

    async def _send_reminder_notification(self, pending: Dict) -> None:
        """
        Send reminder notification for a single pending quiz

        Args:
            pending: dict with user and quiz info
        """
        message = (
            f"Reminder: Complete quiz '{pending['quiz_title']}' "
            f"in {pending['company_name']}. "
            f"You need to take this quiz every 24 hours!"
        )

        notification = await self.notification_repo.create_notification(
            user_id=pending["user_id"],
            message=message,
            notification_type="quiz_reminder",
            related_entity_id=pending["quiz_id"]
        )

        logger.info(
            f"Created reminder notification {notification.id} "
            f"for user {pending['user_username']}"
        )

        try:
            ws_message = {
                "type": "new_notification",
                "notification": {
                    "id": str(notification.id),
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat(),
                    "related_entity_id": str(notification.related_entity_id)
                    if notification.related_entity_id else None
                }
            }

            await manager.send_personal_notification(
                pending["user_id"],
                ws_message
            )

            logger.debug(
                f"Sent WebSocket notification to user {pending['user_username']}"
            )

        except Exception as e:
            logger.warning(
                f"WebSocket send failed for user {pending['user_username']}: {str(e)}"
            )
