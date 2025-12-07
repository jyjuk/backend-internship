from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification model"""

    def __init__(self, session: AsyncSession):
        super().__init__(Notification, session)

    async def get_user_notifications(
            self,
            user_id: UUID,
            skip: int = 0,
            limit: int = 50,
            unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a user"""
        filters = {"user_id": user_id}
        if unread_only:
            filters["is_read"] = False

        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=Notification.created_at.desc()
        )

    async def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread notifications for a user"""
        stmt = select(func.count(Notification.id)).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> Optional[Notification]:
        """Mark a notification as read"""
        notification = await self.get_by_id(notification_id)

        if not notification or notification.user_id != user_id:
            return None

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(notification)

        return notification

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user"""
        from sqlalchemy import update

        stmt = update(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).values(
            is_read=True,
            read_at=datetime.utcnow()
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount

    async def create_notification(
            self,
            user_id: UUID,
            message: str,
            notification_type: str,
            related_entity_id: Optional[UUID] = None
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            message=message,
            notification_type=notification_type,
            related_entity_id=related_entity_id
        )

        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)

        return notification

    async def create_bulk_notifications(
            self,
            notifications_data: List[dict]
    ) -> List[Notification]:
        """Create multiple notifications at once"""
        notifications = [
            Notification(**data)
            for data in notifications_data
        ]

        self.session.add_all(notifications)
        await self.session.commit()

        return notifications
