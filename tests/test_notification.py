from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationBase,
    NotificationCreate,
    NotificationResponse,
    NotificationList,
    UnreadCountResponse
)


def test_notification_service_has_required_methods():
    """Test that NotificationService has all required methods"""
    assert hasattr(NotificationService, 'get_user_notifications')
    assert hasattr(NotificationService, 'get_unread_count')
    assert hasattr(NotificationService, 'mark_notification_as_read')
    assert hasattr(NotificationService, 'mark_all_as_read')
    assert hasattr(NotificationService, 'notify_quiz_created')


def test_notification_schemas():
    """Test that notification schemas have required fields"""
    # NotificationBase
    assert 'message' in NotificationBase.model_fields
    assert 'notification_type' in NotificationBase.model_fields

    # NotificationCreate
    assert 'user_id' in NotificationCreate.model_fields
    assert 'related_entity_id' in NotificationCreate.model_fields
    assert 'message' in NotificationCreate.model_fields
    assert 'notification_type' in NotificationCreate.model_fields

    # NotificationResponse
    assert 'id' in NotificationResponse.model_fields
    assert 'user_id' in NotificationResponse.model_fields
    assert 'message' in NotificationResponse.model_fields
    assert 'notification_type' in NotificationResponse.model_fields
    assert 'is_read' in NotificationResponse.model_fields
    assert 'read_at' in NotificationResponse.model_fields
    assert 'created_at' in NotificationResponse.model_fields
    assert 'updated_at' in NotificationResponse.model_fields

    # NotificationList
    assert 'notifications' in NotificationList.model_fields
    assert 'total' in NotificationList.model_fields
    assert 'total_count' in NotificationList.model_fields

    # UnreadCountResponse
    assert 'unread_count' in UnreadCountResponse.model_fields


def test_notification_create_schema():
    """Test NotificationCreate schema creation"""
    from uuid import uuid4

    user_id = uuid4()
    quiz_id = uuid4()

    notification = NotificationCreate(
        user_id=user_id,
        message="New quiz created",
        notification_type="quiz_created",
        related_entity_id=quiz_id
    )

    assert notification.user_id == user_id
    assert notification.message == "New quiz created"
    assert notification.notification_type == "quiz_created"
    assert notification.related_entity_id == quiz_id


def test_unread_count_response_schema():
    """Test UnreadCountResponse schema"""
    response = UnreadCountResponse(unread_count=5)
    assert response.unread_count == 5