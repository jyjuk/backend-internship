from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import logging
from app.repositories.notification import NotificationRepository
from app.repositories.company_member import CompanyMemberRepository
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationList,
    UnreadCountResponse
)
from app.models.user import User

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification operations"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.notification_repo = NotificationRepository(session)
        self.member_repo = CompanyMemberRepository(session)

    async def get_user_notifications(
            self,
            user: User,
            skip: int = 0,
            limit: int = 50,
            unread_only: bool = False
    ) -> NotificationList:
        """Get notifications for current user"""
        try:
            notifications = await self.notification_repo.get_user_notifications(
                user_id=user.id,
                skip=skip,
                limit=limit,
                unread_only=unread_only
            )

            total = await self.notification_repo.count(filters={"user_id": user.id})
            unread_count = await self.notification_repo.get_unread_count(user.id)

            return NotificationList(
                notifications=[
                    NotificationResponse.model_validate(notif)
                    for notif in notifications
                ],
                total=total,
                total_count=unread_count
            )

        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get notifications"
            )

    async def get_unread_count(self, user: User) -> UnreadCountResponse:
        """Get count of unread notifications"""
        try:
            unread_count = await self.notification_repo.get_unread_count(user.id)
            return UnreadCountResponse(unread_count=unread_count)

        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get unread count"
            )

    async def mark_notification_as_read(
            self,
            notification_id: UUID,
            user: User
    ) -> NotificationResponse:
        """Mark a notification as read"""
        try:
            notification = await self.notification_repo.mark_as_read(
                notification_id=notification_id,
                user_id=user.id
            )

            if not notification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found"
                )

            return NotificationResponse.model_validate(notification)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to mark notification as read"
            )

    async def mark_all_as_read(self, user: User) -> dict:
        """Mark all notifications as read for current user"""
        try:
            updated_count = await self.notification_repo.mark_all_as_read(user.id)

            return {
                "message": "All notifications marked as read",
                "updated_count": updated_count
            }

        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to mark all notifications as read"
            )

    async def notify_quiz_created(
            self,
            quiz_id: UUID,
            quiz_title: str,
            company_id: UUID,
            company_name: str,
            creator_id: UUID
    ) -> int:
        """Send notifications to all company members when a new quiz is created"""
        try:
            members = await self.member_repo.get_company_members(company_id)

            member_ids = [
                member.user_id
                for member in members
                if member.user_id != creator_id
            ]

            if not member_ids:
                return 0

            message = f"New quiz '{quiz_title}' has been created in {company_name}. Take it now!"
            notifications_data = [
                {
                    "user_id": user_id,
                    "message": message,
                    "notification_type": "quiz_created",
                    "related_entity_id": quiz_id
                }
                for user_id in member_ids
            ]

            await self.notification_repo.create_bulk_notifications(notifications_data)

            logger.info(
                f"Created {len(member_ids)} notifications for quiz {quiz_id} "
                f"in company {company_id}"
            )

            return len(member_ids)

        except Exception as e:
            logger.error(f"Error notifying quiz created: {str(e)}")
            return 0
