from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationResponse,
    NotificationList,
    UnreadCountResponse
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationList)
async def get_notifications(
        skip: int = Query(0, ge=0, description="Number of notifications to skip"),
        limit: int = Query(50, ge=1, le=100, description="Number of notifications to return"),
        unread_only: bool = Query(False, description="Return only unread notifications"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get list of notifications for current user"""
    service = NotificationService(db)
    return await service.get_user_notifications(
        user=current_user,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications"""
    service = NotificationService(db)
    return await service.get_unread_count(current_user)


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
        notification_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Mark a notification as read"""
    service = NotificationService(db)
    return await service.mark_notification_as_read(notification_id, current_user)


@router.put("/mark-all-read")
async def mark_all_notifications_as_read(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read"""
    service = NotificationService(db)
    return await service.mark_all_as_read(current_user)
