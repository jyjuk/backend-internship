import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from app.services.scheduled_quiz_reminder import ScheduledQuizReminderService
from app.repositories.scheduled_check import ScheduledCheckRepository


@pytest.mark.asyncio
class TestScheduledQuizReminderService:
    """Tests for ScheduledQuizReminderService"""

    async def test_service_has_required_methods(self):
        """Verify service has all required methods"""
        assert hasattr(ScheduledQuizReminderService, 'check_and_notify_pending_quizzes')
        assert hasattr(ScheduledQuizReminderService, '_send_reminder_notification')

    async def test_check_and_notify_returns_stats(self):
        """Test that check_and_notify returns proper stats dict"""
        mock_session = AsyncMock()

        with patch.object(ScheduledCheckRepository, 'get_users_pending_quizzes', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            service = ScheduledQuizReminderService(mock_session)
            stats = await service.check_and_notify_pending_quizzes()

            assert isinstance(stats, dict)
            assert "users_checked" in stats
            assert "pending_quizzes" in stats
            assert "notifications_sent" in stats
            assert "errors" in stats

    async def test_check_with_no_pending_quizzes(self):
        """Test check when no pending quizzes exist"""
        mock_session = AsyncMock()

        with patch.object(ScheduledCheckRepository, 'get_users_pending_quizzes', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            service = ScheduledQuizReminderService(mock_session)
            stats = await service.check_and_notify_pending_quizzes()

            assert stats["pending_quizzes"] == 0
            assert stats["notifications_sent"] == 0
            assert stats["users_checked"] == 0


@pytest.mark.asyncio
class TestScheduledCheckRepository:
    """Tests for ScheduledCheckRepository"""

    async def test_repository_has_required_methods(self):
        """Verify repository has all required methods"""
        assert hasattr(ScheduledCheckRepository, 'get_all_active_users')
        assert hasattr(ScheduledCheckRepository, 'get_user_available_quizzes')
        assert hasattr(ScheduledCheckRepository, 'get_last_quiz_attempt_time')
        assert hasattr(ScheduledCheckRepository, 'get_users_pending_quizzes')
        assert hasattr(ScheduledCheckRepository, 'get_company_name')


def test_scheduler_module_imports():
    """Test that scheduler module can be imported"""
    from app.core.scheduler import scheduler, start_scheduler, shutdown_scheduler

    assert scheduler is not None
    assert callable(start_scheduler)
    assert callable(shutdown_scheduler)


def test_scheduled_job_function_exists():
    """Test that scheduled job function exists"""
    from app.core.scheduler import scheduled_quiz_reminder_job

    assert callable(scheduled_quiz_reminder_job)
