from pydantic import BaseModel, Field, ConfigDict, field_serializer
from uuid import UUID
from datetime import datetime
from typing import Optional


class NotificationBase(BaseModel):
    """Base notification schema"""
    message: str = Field(..., max_length=500, description="Notification message")
    notification_type: str = Field(..., max_length=50, description="Type of notification")


class NotificationCreate(NotificationBase):
    """Schema for creating notification"""
    user_id: UUID
    related_entity_id: Optional[UUID] = None


class NotificationResponse(NotificationBase):
    """Schema for notification response"""
    id: UUID
    user_id: UUID
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("id", "user_id")
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)


class NotificationList(BaseModel):
    """Schema for list of notifications"""
    notifications: list[NotificationResponse]
    total: int
    total_count: int


class NotificationMarkRead(BaseModel):
    """Schema for marking notification as read"""
    is_read: bool = True


class UnreadCountResponse(BaseModel):
    """Schema for unread count response"""
    unread_count: int
