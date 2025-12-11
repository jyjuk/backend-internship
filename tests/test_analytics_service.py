import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from app.services.analytics_service import AnalyticsService
from app.repositories.quiz_attempt import QuizAttemptRepository
from app.repositories.company import CompanyRepository
from app.repositories.company_member import CompanyMemberRepository
from app.repositories.quiz import QuizRepository
from app.models.user import User
from app.models.company import Company
from app.models.company_member import CompanyMember
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz import Quiz


@pytest.mark.asyncio
class TestAnalyticsService:
    """Tests for AnalyticsService"""

    async def test_check_owner_or_admin_owner_has_access(self):
        """Test that company owner has access"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=owner_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_company

            service = AnalyticsService(mock_session)
            await service._check_owner_or_admin(company_id, owner_id)

            mock_get.assert_called_once_with(company_id)

    async def test_check_owner_or_admin_admin_has_access(self):
        """Test that company admin has access"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        admin_id = uuid4()

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=owner_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_member = CompanyMember(
            id=uuid4(),
            user_id=admin_id,
            company_id=company_id,
            is_admin=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                mock_get_company.return_value = mock_company
                mock_get_member.return_value = mock_member

                service = AnalyticsService(mock_session)
                await service._check_owner_or_admin(company_id, admin_id)

    async def test_check_owner_or_admin_regular_member_forbidden(self):
        """Test that regular member gets 403"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        member_id = uuid4()

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=owner_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_member = CompanyMember(
            id=uuid4(),
            user_id=member_id,
            company_id=company_id,
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                mock_get_company.return_value = mock_company
                mock_get_member.return_value = mock_member

                service = AnalyticsService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service._check_owner_or_admin(company_id, member_id)

                assert exc_info.value.status_code == 403
                assert "Only company owner or admin" in exc_info.value.detail

    async def test_get_user_overall_analytics_success(self):
        """Test getting user overall analytics"""
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

        mock_stats = {
            "average_score": 85.5,
            "total_attempts": 20,
            "total_companies": 3,
            "total_quizzes": 10
        }

        with patch.object(QuizAttemptRepository, 'get_user_overall_stats_sql',
                          new_callable=AsyncMock) as mock_get_stats:
            mock_get_stats.return_value = mock_stats

            service = AnalyticsService(mock_session)
            result = await service.get_user_overall_analytics(mock_user)

            assert result.average_score == 85.5
            assert result.total_attempts == 20
            assert result.total_companies == 3
            assert result.total_quizzes_taken == 10

    async def test_get_user_quiz_analytics_success(self):
        """Test getting user quiz analytics"""
        mock_session = AsyncMock()
        user_id = uuid4()
        quiz_id = uuid4()
        company_id = uuid4()

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

        mock_quiz_stats = [
            {
                "quiz_id": quiz_id,
                "average_score": 80.0,
                "attempts_count": 5,
                "last_attempt_at": datetime.now(timezone.utc)
            }
        ]

        mock_quiz = Quiz(
            id=quiz_id,
            company_id=company_id,
            title="Test Quiz",
            frequency=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=uuid4(),
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_attempt = QuizAttempt(
            id=uuid4(),
            user_id=user_id,
            quiz_id=quiz_id,
            company_id=company_id,
            score=8,
            total_questions=10,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        mock_attempt.quiz = mock_quiz
        mock_attempt.company = mock_company

        with patch.object(QuizAttemptRepository, 'get_user_quiz_stats_sql', new_callable=AsyncMock) as mock_get_stats:
            with patch.object(QuizAttemptRepository, 'get_user_quiz_attempts_with_relations',
                              new_callable=AsyncMock) as mock_get_attempts:
                mock_get_stats.return_value = mock_quiz_stats
                mock_get_attempts.return_value = [mock_attempt]

                service = AnalyticsService(mock_session)
                result = await service.get_user_quiz_analytics(mock_user)

                assert len(result.quizzes) == 1
                assert result.quizzes[0].quiz_id == quiz_id
                assert result.quizzes[0].average_score == 80.0

    async def test_get_company_overview_analytics_success(self):
        """Test owner getting company overview analytics"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()

        mock_owner = User(
            id=owner_id,
            email="owner@test.com",
            username="owner",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=owner_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_stats = {
            "total_attempts": 100,
            "average_score": 75.5
        }

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'count_by_company',
                              new_callable=AsyncMock) as mock_count_members:
                with patch.object(QuizRepository, 'count_by_company', new_callable=AsyncMock) as mock_count_quizzes:
                    with patch.object(QuizAttemptRepository, 'get_company_overview_stats_sql',
                                      new_callable=AsyncMock) as mock_get_stats:
                        with patch.object(QuizAttemptRepository, 'get_by_company',
                                          new_callable=AsyncMock) as mock_get_attempts:
                            mock_get_company.return_value = mock_company
                            mock_count_members.return_value = 10
                            mock_count_quizzes.return_value = 5
                            mock_get_stats.return_value = mock_stats
                            mock_get_attempts.return_value = []

                            service = AnalyticsService(mock_session)
                            result = await service.get_company_overview_analytics(company_id, mock_owner)

                            assert result.company_id == company_id
                            assert result.company_name == "Test Company"
                            assert result.total_members == 10
                            assert result.total_quizzes == 5
                            assert result.total_attempts == 100
                            assert result.average_company_score == 75.5

    async def test_get_company_overview_analytics_forbidden(self):
        """Test regular member cannot access company analytics"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        member_id = uuid4()

        mock_member_user = User(
            id=member_id,
            email="member@test.com",
            username="member",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=owner_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_member = CompanyMember(
            id=uuid4(),
            user_id=member_id,
            company_id=company_id,
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                mock_get_company.return_value = mock_company
                mock_get_member.return_value = mock_member

                service = AnalyticsService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.get_company_overview_analytics(company_id, mock_member_user)

                assert exc_info.value.status_code == 403

    async def test_get_company_members_analytics_success(self):
        """Test getting company members analytics"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        member_id = uuid4()

        mock_owner = User(
            id=owner_id,
            email="owner@test.com",
            username="owner",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=owner_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_member_user = User(
            id=member_id,
            email="member@test.com",
            username="member",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_member = CompanyMember(
            id=uuid4(),
            user_id=member_id,
            company_id=company_id,
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        mock_member.user = mock_member_user

        mock_members_stats = [
            {
                "user_id": member_id,
                "total_attempts": 15,
                "average_score": 82.0,
                "last_attempt_at": datetime.now(timezone.utc)
            }
        ]

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_company_with_user',
                              new_callable=AsyncMock) as mock_get_members:
                with patch.object(QuizAttemptRepository, 'get_company_members_stats_sql',
                                  new_callable=AsyncMock) as mock_get_stats:
                    mock_get_company.return_value = mock_company
                    mock_get_members.return_value = [mock_member]
                    mock_get_stats.return_value = mock_members_stats

                    service = AnalyticsService(mock_session)
                    result = await service.get_company_members_analytics(company_id, mock_owner)

                    assert len(result.members) == 1
                    assert result.members[0].user_id == member_id
                    assert result.members[0].total_attempts == 15
                    assert result.members[0].average_score == 82.0
