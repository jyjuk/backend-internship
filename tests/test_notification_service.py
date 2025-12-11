import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from app.services.notification_service import NotificationService
from app.repositories.notification import NotificationRepository
from app.repositories.company_member import CompanyMemberRepository
from app.models.user import User
from app.models.notification import Notification
from app.models.company_member import CompanyMember


@pytest.mark.asyncio
class TestNotificationService:
    """Tests for NotificationService"""

    async def test_get_user_notifications_success(self):
        """Test getting user notifications returns list"""
        mock_session = AsyncMock()
        user_id = uuid4()

        mock_user = User(
            id=user_id,
            email="user@test.com",
            username="user",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_notifications = [
            Notification(
                id=uuid4(),
                user_id=user_id,
                message="Test notification",
                notification_type="quiz_created",
                is_read=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        ]

        with patch.object(NotificationRepository, 'get_user_notifications',
                          new_callable=AsyncMock) as mock_get_notifications:
            with patch.object(NotificationRepository, 'count', new_callable=AsyncMock) as mock_count:
                with patch.object(NotificationRepository, 'get_unread_count',
                                  new_callable=AsyncMock) as mock_unread_count:
                    mock_get_notifications.return_value = mock_notifications
                    mock_count.return_value = 1
                    mock_unread_count.return_value = 1

                    service = NotificationService(mock_session)
                    result = await service.get_user_notifications(mock_user, skip=0, limit=50)

                    assert result.total == 1
                    assert result.total_count == 1
                    assert len(result.notifications) == 1

    async def test_get_unread_count_success(self):
        """Test getting unread count"""
        mock_session = AsyncMock()
        user_id = uuid4()

        mock_user = User(
            id=user_id,
            email="user@test.com",
            username="user",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(NotificationRepository, 'get_unread_count', new_callable=AsyncMock) as mock_unread_count:
            mock_unread_count.return_value = 5

            service = NotificationService(mock_session)
            result = await service.get_unread_count(mock_user)

            assert result.unread_count == 5

    async def test_mark_notification_as_read_success(self):
        """Test successfully marking notification as read"""
        mock_session = AsyncMock()
        user_id = uuid4()
        notification_id = uuid4()

        mock_user = User(
            id=user_id,
            email="user@test.com",
            username="user",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_notification = Notification(
            id=notification_id,
            user_id=user_id,
            message="Test notification",
            notification_type="quiz_created",
            is_read=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(NotificationRepository, 'mark_as_read', new_callable=AsyncMock) as mock_mark_as_read:
            mock_mark_as_read.return_value = mock_notification

            service = NotificationService(mock_session)
            result = await service.mark_notification_as_read(notification_id, mock_user)

            assert result.id == notification_id
            assert result.is_read == True

    async def test_mark_notification_as_read_not_found(self):
        """Test mark as read fails when notification doesn't exist"""
        mock_session = AsyncMock()
        user_id = uuid4()
        notification_id = uuid4()

        mock_user = User(
            id=user_id,
            email="user@test.com",
            username="user",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(NotificationRepository, 'mark_as_read', new_callable=AsyncMock) as mock_mark_as_read:
            mock_mark_as_read.return_value = None

            service = NotificationService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.mark_notification_as_read(notification_id, mock_user)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Notification not found"

    async def test_mark_all_as_read_success(self):
        """Test successfully marking all notifications as read"""
        mock_session = AsyncMock()
        user_id = uuid4()

        mock_user = User(
            id=user_id,
            email="user@test.com",
            username="user",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(NotificationRepository, 'mark_all_as_read', new_callable=AsyncMock) as mock_mark_all:
            mock_mark_all.return_value = 3

            service = NotificationService(mock_session)
            result = await service.mark_all_as_read(mock_user)

            assert result["updated_count"] == 3
            assert result["message"] == "All notifications marked as read"

    async def test_notify_quiz_created_success(self):
        """Test successfully creating notifications for quiz"""
        mock_session = AsyncMock()
        quiz_id = uuid4()
        company_id = uuid4()
        creator_id = uuid4()
        member1_id = uuid4()
        member2_id = uuid4()

        mock_members = [
            CompanyMember(
                id=uuid4(),
                user_id=creator_id,
                company_id=company_id,
                is_admin=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            ),
            CompanyMember(
                id=uuid4(),
                user_id=member1_id,
                company_id=company_id,
                is_admin=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            ),
            CompanyMember(
                id=uuid4(),
                user_id=member2_id,
                company_id=company_id,
                is_admin=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        ]

        notification1 = Notification(
            id=uuid4(),
            user_id=member1_id,
            message="New quiz 'Test Quiz' has been created in Test Company. Take it now!",
            notification_type="quiz_created",
            is_read=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        notification1.related_entity_id = quiz_id

        notification2 = Notification(
            id=uuid4(),
            user_id=member2_id,
            message="New quiz 'Test Quiz' has been created in Test Company. Take it now!",
            notification_type="quiz_created",
            is_read=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        notification2.related_entity_id = quiz_id

        created_notifications = [notification1, notification2]

        with patch.object(CompanyMemberRepository, 'get_company_members', new_callable=AsyncMock) as mock_get_members:
            with patch.object(NotificationRepository, 'create_bulk_notifications',
                              new_callable=AsyncMock) as mock_create_bulk:
                with patch('app.core.websocket.manager') as mock_manager:
                    mock_get_members.return_value = mock_members
                    mock_create_bulk.return_value = created_notifications
                    mock_manager.send_personal_notification = AsyncMock()

                    service = NotificationService(mock_session)
                    result = await service.notify_quiz_created(
                        quiz_id=quiz_id,
                        quiz_title="Test Quiz",
                        company_id=company_id,
                        company_name="Test Company",
                        creator_id=creator_id
                    )

                    assert result == 2
                    mock_create_bulk.assert_called_once()
                    assert mock_manager.send_personal_notification.call_count == 2

    async def test_notify_quiz_created_no_members(self):
        """Test notify returns 0 when no members to notify"""
        mock_session = AsyncMock()
        quiz_id = uuid4()
        company_id = uuid4()
        creator_id = uuid4()

        mock_members = [
            CompanyMember(
                id=uuid4(),
                user_id=creator_id,
                company_id=company_id,
                is_admin=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        ]

        with patch.object(CompanyMemberRepository, 'get_company_members', new_callable=AsyncMock) as mock_get_members:
            mock_get_members.return_value = mock_members

            service = NotificationService(mock_session)
            result = await service.notify_quiz_created(
                quiz_id=quiz_id,
                quiz_title="Test Quiz",
                company_id=company_id,
                company_name="Test Company",
                creator_id=creator_id
            )

            assert result == 0

    async def test_notify_quiz_created_skips_creator(self):
        """Test notify skips the creator"""
        mock_session = AsyncMock()
        quiz_id = uuid4()
        company_id = uuid4()
        creator_id = uuid4()
        member_id = uuid4()

        mock_members = [
            CompanyMember(
                id=uuid4(),
                user_id=creator_id,
                company_id=company_id,
                is_admin=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            ),
            CompanyMember(
                id=uuid4(),
                user_id=member_id,
                company_id=company_id,
                is_admin=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        ]

        notification = Notification(
            id=uuid4(),
            user_id=member_id,
            message="New quiz 'Test Quiz' has been created in Test Company. Take it now!",
            notification_type="quiz_created",
            is_read=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        notification.related_entity_id = quiz_id

        created_notification = [notification]

        with patch.object(CompanyMemberRepository, 'get_company_members', new_callable=AsyncMock) as mock_get_members:
            with patch.object(NotificationRepository, 'create_bulk_notifications',
                              new_callable=AsyncMock) as mock_create_bulk:
                with patch('app.core.websocket.manager') as mock_manager:
                    mock_get_members.return_value = mock_members
                    mock_create_bulk.return_value = created_notification
                    mock_manager.send_personal_notification = AsyncMock()

                    service = NotificationService(mock_session)
                    result = await service.notify_quiz_created(
                        quiz_id=quiz_id,
                        quiz_title="Test Quiz",
                        company_id=company_id,
                        company_name="Test Company",
                        creator_id=creator_id
                    )

                    assert result == 1
