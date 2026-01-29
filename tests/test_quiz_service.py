import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from app.services.quiz_service import QuizService
from app.repositories.company import CompanyRepository
from app.repositories.company_member import CompanyMemberRepository
from app.repositories.quiz import QuizRepository
from app.repositories.question import QuestionRepository
from app.repositories.answer import AnswerRepository
from app.models.user import User
from app.models.company import Company
from app.models.company_member import CompanyMember
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.schemas.quiz import QuizCreate, QuizUpdate, QuestionCreate, AnswerCreate


@pytest.mark.asyncio
class TestQuizService:
    """Tests for QuizService"""

    async def test_check_owner_or_admin_owner_has_access(self):
        """Test that company owner has access"""
        mock_session = AsyncMock()
        company_id = uuid4()
        user_id = uuid4()

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=user_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_company

            service = QuizService(mock_session)
            await service._check_owner_or_admin(company_id, user_id)

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

                service = QuizService(mock_session)
                await service._check_owner_or_admin(company_id, admin_id)

    async def test_check_owner_or_admin_company_not_found(self):
        """Test that 404 raised when company doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()
        user_id = uuid4()

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            service = QuizService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service._check_owner_or_admin(company_id, user_id)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Company not found"

    async def test_check_owner_or_admin_regular_member_forbidden(self):
        """Test that regular member without admin rights gets 403"""
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

                service = QuizService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service._check_owner_or_admin(company_id, member_id)

                assert exc_info.value.status_code == 403
                assert exc_info.value.detail == "Only company owner or admin can perform this action"

    async def test_create_quiz_success_by_owner(self):
        """Test owner successfully creates quiz"""
        mock_session = AsyncMock()
        company_id = uuid4()
        user_id = uuid4()

        mock_user = User(
            id=user_id,
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
            owner_id=user_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        quiz_data = QuizCreate(
            title="Test Quiz",
            description="Test Description",
            questions=[
                QuestionCreate(
                    title="Question 1",
                    order=0,
                    answers=[
                        AnswerCreate(text="Answer 1", is_correct=True, order=0),
                        AnswerCreate(text="Answer 2", is_correct=False, order=1)
                    ]
                ),
                QuestionCreate(
                    title="Question 2",
                    order=1,
                    answers=[
                        AnswerCreate(text="Answer 3", is_correct=True, order=0),
                        AnswerCreate(text="Answer 4", is_correct=False, order=1)
                    ]
                )
            ]
        )

        created_quiz = Quiz(
            id=uuid4(),
            company_id=company_id,
            title="Test Quiz",
            description="Test Description",
            frequency=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(QuizRepository, 'create', new_callable=AsyncMock) as mock_create_quiz:
                with patch.object(QuestionRepository, 'create', new_callable=AsyncMock) as mock_create_question:
                    with patch.object(AnswerRepository, 'create', new_callable=AsyncMock) as mock_create_answer:
                        with patch.object(QuizRepository, 'get_quiz_with_questions',
                                          new_callable=AsyncMock) as mock_get_quiz:
                            with patch('app.services.notification_service.NotificationService') as mock_notif_service:
                                mock_get_company.return_value = mock_company
                                mock_create_quiz.return_value = created_quiz

                                created_question = Question(
                                    id=uuid4(),
                                    quiz_id=created_quiz.id,
                                    title="Question 1",
                                    order=0,
                                    created_at=datetime.now(timezone.utc),
                                    updated_at=datetime.now(timezone.utc)
                                )
                                mock_create_question.return_value = created_question

                                created_quiz.questions = [created_question]
                                mock_get_quiz.return_value = created_quiz

                                mock_notif_instance = AsyncMock()
                                mock_notif_instance.notify_quiz_created = AsyncMock(return_value=5)
                                mock_notif_service.return_value = mock_notif_instance

                                service = QuizService(mock_session)
                                result = await service.create_quiz(company_id, quiz_data, mock_user)

                                assert result.title == "Test Quiz"
                                mock_create_quiz.assert_called_once()
                                assert mock_create_question.call_count == 2
                                assert mock_create_answer.call_count == 4

    async def test_create_quiz_forbidden_for_regular_member(self):
        """Test regular member cannot create quiz"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        member_id = uuid4()

        mock_user = User(
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

        quiz_data = QuizCreate(
            title="Test Quiz",
            questions=[
                QuestionCreate(
                    title="Question 1",
                    order=0,
                    answers=[
                        AnswerCreate(text="Answer 1", is_correct=True, order=0),
                        AnswerCreate(text="Answer 2", is_correct=False, order=1)
                    ]
                ),
                QuestionCreate(
                    title="Question 2",
                    order=1,
                    answers=[
                        AnswerCreate(text="Answer 3", is_correct=True, order=0),
                        AnswerCreate(text="Answer 4", is_correct=False, order=1)
                    ]
                )
            ]
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                mock_get_company.return_value = mock_company
                mock_get_member.return_value = mock_member

                service = QuizService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.create_quiz(company_id, quiz_data, mock_user)

                assert exc_info.value.status_code == 403

    async def test_delete_quiz_success_by_owner(self):
        """Test owner successfully deletes quiz"""
        mock_session = AsyncMock()
        company_id = uuid4()
        quiz_id = uuid4()
        user_id = uuid4()

        mock_user = User(
            id=user_id,
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
            owner_id=user_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_quiz = Quiz(
            id=quiz_id,
            company_id=company_id,
            title="Test Quiz",
            frequency=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(QuizRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_quiz:
                with patch.object(QuizRepository, 'delete', new_callable=AsyncMock) as mock_delete:
                    mock_get_company.return_value = mock_company
                    mock_get_quiz.return_value = mock_quiz

                    service = QuizService(mock_session)
                    await service.delete_quiz(company_id, quiz_id, mock_user)

                    mock_delete.assert_called_once_with(mock_quiz)

    async def test_delete_quiz_not_found(self):
        """Test delete fails when quiz doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()
        quiz_id = uuid4()
        user_id = uuid4()

        mock_user = User(
            id=user_id,
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
            owner_id=user_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(QuizRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_quiz:
                mock_get_company.return_value = mock_company
                mock_get_quiz.return_value = None

                service = QuizService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.delete_quiz(company_id, quiz_id, mock_user)

                assert exc_info.value.status_code == 404
                assert exc_info.value.detail == "Quiz not found"

    async def test_get_company_quizzes_success(self):
        """Test getting company quizzes returns list"""
        mock_session = AsyncMock()
        company_id = uuid4()

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=uuid4(),
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_quiz = Quiz(
            id=uuid4(),
            company_id=company_id,
            title="Test Quiz",
            frequency=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        mock_quiz.questions = []

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(QuizRepository, 'get_company_quizzes', new_callable=AsyncMock) as mock_get_quizzes:
                with patch.object(QuizRepository, 'count_company_quizzes', new_callable=AsyncMock) as mock_count:
                    with patch.object(QuizRepository, 'get_quiz_with_questions',
                                      new_callable=AsyncMock) as mock_get_complete:
                        mock_get_company.return_value = mock_company
                        mock_get_quizzes.return_value = [mock_quiz]
                        mock_count.return_value = 1
                        mock_get_complete.return_value = mock_quiz

                        service = QuizService(mock_session)
                        result = await service.get_company_quizzes(company_id, skip=0, limit=100)

                        assert result.total == 1
                        assert len(result.quizzes) == 1

    async def test_get_company_quizzes_company_not_found(self):
        """Test get quizzes fails when company doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            service = QuizService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.get_company_quizzes(company_id)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Company not found"

    async def test_get_quiz_success(self):
        """Test getting quiz by ID returns quiz with questions"""
        mock_session = AsyncMock()
        company_id = uuid4()
        quiz_id = uuid4()

        mock_quiz = Quiz(
            id=quiz_id,
            company_id=company_id,
            title="Test Quiz",
            frequency=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        mock_quiz.questions = []

        with patch.object(QuizRepository, 'get_quiz_with_questions', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_quiz

            service = QuizService(mock_session)
            result = await service.get_quiz(company_id, quiz_id)

            assert result.id == quiz_id
            assert result.title == "Test Quiz"

    async def test_get_quiz_not_found(self):
        """Test get quiz fails when quiz doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()
        quiz_id = uuid4()

        with patch.object(QuizRepository, 'get_quiz_with_questions', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            service = QuizService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.get_quiz(company_id, quiz_id)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Quiz not found"
