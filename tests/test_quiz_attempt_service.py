import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException

from app.services.quiz_attempt_service import QuizAttemptService
from app.repositories.quiz import QuizRepository
from app.repositories.company import CompanyRepository
from app.repositories.quiz_attempt import QuizAttemptRepository

from app.models.user import User
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.models.quiz_attempt import QuizAttempt

from app.schemas.quiz import QuizSubmission, AnswerSubmission


@pytest.mark.asyncio
class TestQuizAttemptService:

    async def test_submit_quiz_all_correct_answers(self):
        mock_session = AsyncMock()
        company_id = uuid4()
        quiz_id = uuid4()
        user_id = uuid4()

        mock_user = User(
            id=user_id,
            email="user@test.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        q1_id = uuid4()
        q2_id = uuid4()
        a1_id = uuid4()
        a2_id = uuid4()

        quiz = Quiz(
            id=quiz_id,
            company_id=company_id,
            title="Quiz",
            frequency=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        q1 = Question(
            id=q1_id,
            quiz_id=quiz_id,
            title="Q1",
            order=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        q1.answers = [
            Answer(id=a1_id, question_id=q1_id, text="Correct", is_correct=True, order=0),
            Answer(id=uuid4(), question_id=q1_id, text="Wrong", is_correct=False, order=1),
        ]

        q2 = Question(
            id=q2_id,
            quiz_id=quiz_id,
            title="Q2",
            order=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        q2.answers = [
            Answer(id=a2_id, question_id=q2_id, text="Correct", is_correct=True, order=0),
            Answer(id=uuid4(), question_id=q2_id, text="Wrong", is_correct=False, order=1),
        ]

        quiz.questions = [q1, q2]

        submission = QuizSubmission(
            answers=[
                AnswerSubmission(question_id=q1_id, answer_ids=[a1_id]),
                AnswerSubmission(question_id=q2_id, answer_ids=[a2_id]),
            ]
        )

        created_attempt = QuizAttempt(
            id=uuid4(),
            user_id=user_id,
            quiz_id=quiz_id,
            company_id=company_id,
            score=2,
            total_questions=2,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        with patch.object(QuizRepository, "get_quiz_with_questions", new_callable=AsyncMock) as mock_get:
            with patch.object(QuizAttemptRepository, "create", new_callable=AsyncMock) as mock_create:
                with patch.object(QuizRepository, "update", new_callable=AsyncMock):
                    with patch("app.services.quiz_attempt_service.RedisService.store_quiz_response",
                               new_callable=AsyncMock) as mock_redis:
                        mock_get.return_value = quiz
                        mock_create.return_value = created_attempt

                        service = QuizAttemptService(mock_session)
                        result = await service.submit_quiz(company_id, quiz_id, submission, mock_user)

                        assert result.score == 2
                        assert result.percentage == 100.0
                        assert mock_redis.call_count == 2

    async def test_submit_quiz_partial_correct_answers(self):
        mock_session = AsyncMock()
        company_id = uuid4()
        quiz_id = uuid4()
        user_id = uuid4()

        mock_user = User(
            id=user_id,
            email="user@test.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        q1_id = uuid4()
        q2_id = uuid4()
        correct_id = uuid4()
        wrong_id = uuid4()

        quiz = Quiz(
            id=quiz_id,
            company_id=company_id,
            title="Quiz",
            frequency=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        q1 = Question(
            id=q1_id,
            quiz_id=quiz_id,
            title="Q1",
            order=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        q1.answers = [
            Answer(id=correct_id, question_id=q1_id, text="Correct", is_correct=True, order=0),
            Answer(id=uuid4(), question_id=q1_id, text="Wrong", is_correct=False, order=1),
        ]

        q2 = Question(
            id=q2_id,
            quiz_id=quiz_id,
            title="Q2",
            order=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        q2.answers = [
            Answer(id=uuid4(), question_id=q2_id, text="Correct", is_correct=True, order=0),
            Answer(id=wrong_id, question_id=q2_id, text="Wrong", is_correct=False, order=1),
        ]

        quiz.questions = [q1, q2]

        submission = QuizSubmission(
            answers=[
                AnswerSubmission(question_id=q1_id, answer_ids=[correct_id]),
                AnswerSubmission(question_id=q2_id, answer_ids=[wrong_id]),
            ]
        )

        created_attempt = QuizAttempt(
            id=uuid4(),
            user_id=user_id,
            quiz_id=quiz_id,
            company_id=company_id,
            score=1,
            total_questions=2,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        with patch.object(QuizRepository, "get_quiz_with_questions", new_callable=AsyncMock) as mock_get:
            with patch.object(QuizAttemptRepository, "create", new_callable=AsyncMock) as mock_create:
                with patch("app.services.quiz_attempt_service.RedisService.store_quiz_response",
                           new_callable=AsyncMock):
                    mock_get.return_value = quiz
                    mock_create.return_value = created_attempt

                    service = QuizAttemptService(mock_session)
                    result = await service.submit_quiz(company_id, quiz_id, submission, mock_user)

                    assert result.score == 1
                    assert result.percentage == 50.0

    async def test_submit_quiz_not_found(self):
        mock_session = AsyncMock()
        company_id = uuid4()
        quiz_id = uuid4()

        user = User(
            id=uuid4(),
            email="user@test.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        submission = QuizSubmission(answers=[
            AnswerSubmission(question_id=uuid4(), answer_ids=[uuid4()])
        ])

        with patch.object(QuizRepository, "get_quiz_with_questions", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            service = QuizAttemptService(mock_session)

            with pytest.raises(HTTPException) as exc:
                await service.submit_quiz(company_id, quiz_id, submission, user)

            assert exc.value.status_code == 404
            assert exc.value.detail == "Quiz not found"

    async def test_submit_quiz_all_wrong_answers(self):
        """Test submitting quiz with all wrong answers"""
        mock_session = AsyncMock()
        company_id = uuid4()
        quiz_id = uuid4()
        user_id = uuid4()

        mock_user = User(
            id=user_id,
            email="user@test.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        q1_id = uuid4()
        wrong1_id = uuid4()

        quiz = Quiz(
            id=quiz_id,
            company_id=company_id,
            title="Test Quiz",
            frequency=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        q1 = Question(
            id=q1_id,
            quiz_id=quiz_id,
            title="Question 1",
            order=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        q1.answers = [
            Answer(id=uuid4(), question_id=q1_id, text="Correct", is_correct=True, order=0),
            Answer(id=wrong1_id, question_id=q1_id, text="Wrong", is_correct=False, order=1)
        ]

        q2_id = uuid4()
        wrong2_id = uuid4()

        q2 = Question(
            id=q2_id,
            quiz_id=quiz_id,
            title="Question 2",
            order=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        q2.answers = [
            Answer(id=uuid4(), question_id=q2_id, text="Correct", is_correct=True, order=0),
            Answer(id=wrong2_id, question_id=q2_id, text="Wrong", is_correct=False, order=1)
        ]

        quiz.questions = [q1, q2]

        submission = QuizSubmission(
            answers=[
                AnswerSubmission(question_id=q1_id, answer_ids=[wrong1_id]),
                AnswerSubmission(question_id=q2_id, answer_ids=[wrong2_id])
            ]
        )

        created_attempt = QuizAttempt(
            id=uuid4(),
            user_id=user_id,
            quiz_id=quiz_id,
            company_id=company_id,
            score=0,
            total_questions=2,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(QuizRepository, 'get_quiz_with_questions', new_callable=AsyncMock) as mock_get:
            with patch.object(QuizAttemptRepository, 'create', new_callable=AsyncMock) as mock_create:
                with patch.object(QuizRepository, 'update', new_callable=AsyncMock):
                    with patch('app.services.quiz_attempt_service.RedisService.store_quiz_response',
                               new_callable=AsyncMock):
                        mock_get.return_value = quiz
                        mock_create.return_value = created_attempt

                        service = QuizAttemptService(mock_session)
                        result = await service.submit_quiz(company_id, quiz_id, submission, mock_user)

                        assert result.score == 0
                        assert result.percentage == 0.0

    async def test_submit_quiz_missing_answers(self):
        """Test submit fails when not all questions are answered"""
        mock_session = AsyncMock()
        company_id = uuid4()
        quiz_id = uuid4()

        mock_user = User(
            id=uuid4(),
            email="user@test.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        q1_id = uuid4()
        q2_id = uuid4()

        quiz = Quiz(
            id=quiz_id,
            company_id=company_id,
            title="Test Quiz",
            frequency=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        q1 = Question(
            id=q1_id,
            quiz_id=quiz_id,
            title="Question 1",
            order=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        q1.answers = []

        q2 = Question(
            id=q2_id,
            quiz_id=quiz_id,
            title="Question 2",
            order=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        q2.answers = []

        quiz.questions = [q1, q2]

        submission = QuizSubmission(
            answers=[
                AnswerSubmission(question_id=q1_id, answer_ids=[uuid4()])
            ]
        )

        with patch.object(QuizRepository, 'get_quiz_with_questions', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = quiz

            service = QuizAttemptService(mock_session)

            with pytest.raises(HTTPException) as exc:
                await service.submit_quiz(company_id, quiz_id, submission, mock_user)

            assert exc.value.status_code == 400
            assert exc.value.detail == "Must answer all questions"

    async def test_get_user_company_stats_success(self):
        """Test getting user stats for specific company"""
        mock_session = AsyncMock()
        company_id = uuid4()
        user_id = uuid4()

        mock_user = User(
            id=user_id,
            email="user@test.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        from app.models.company import Company

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=uuid4(),
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        stats_data = {
            "total_attempts": 10,
            "total_questions": 100,
            "total_correct": 80,
            "last_attempt": datetime.now(timezone.utc)
        }

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(QuizAttemptRepository, 'get_user_company_stats',
                              new_callable=AsyncMock) as mock_get_stats:
                mock_get_company.return_value = mock_company
                mock_get_stats.return_value = stats_data

                service = QuizAttemptService(mock_session)
                result = await service.get_user_company_stats(company_id, mock_user)

                assert result.company_id == company_id
                assert result.company_name == "Test Company"
                assert result.stats.total_attempts == 10
                assert result.stats.average_score == 80.0

    async def test_get_user_company_stats_zero_division(self):
        """Test stats with zero attempts (no division by zero)"""
        mock_session = AsyncMock()
        company_id = uuid4()

        mock_user = User(
            id=uuid4(),
            email="user@test.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        from app.models.company import Company

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=uuid4(),
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        stats_data = {
            "total_attempts": 0,
            "total_questions": 0,
            "total_correct": 0,
            "last_attempt": None
        }

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(QuizAttemptRepository, 'get_user_company_stats',
                              new_callable=AsyncMock) as mock_get_stats:
                mock_get_company.return_value = mock_company
                mock_get_stats.return_value = stats_data

                service = QuizAttemptService(mock_session)
                result = await service.get_user_company_stats(company_id, mock_user)

                assert result.stats.average_score == 0.0

    async def test_get_user_company_stats_company_not_found(self):
        """Test stats fails when company doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()

        mock_user = User(
            id=uuid4(),
            email="user@test.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            mock_get_company.return_value = None

            service = QuizAttemptService(mock_session)

            with pytest.raises(HTTPException) as exc:
                await service.get_user_company_stats(company_id, mock_user)

            assert exc.value.status_code == 404
            assert exc.value.detail == "Company not found"

    async def test_get_user_system_stats_success(self):
        """Test getting user stats across all companies"""
        mock_session = AsyncMock()

        mock_user = User(
            id=uuid4(),
            email="user@test.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        stats_data = {
            "total_attempts": 50,
            "total_questions": 500,
            "total_correct": 400,
            "last_attempt": datetime.now(timezone.utc),
            "companies_count": 5
        }

        with patch.object(QuizAttemptRepository, 'get_user_system_stats', new_callable=AsyncMock) as mock_get_stats:
            mock_get_stats.return_value = stats_data

            service = QuizAttemptService(mock_session)
            result = await service.get_user_system_stats(mock_user)

            assert result.stats.total_attempts == 50
            assert result.stats.average_score == 80.0
            assert result.companies_participated == 5

    async def test_get_user_system_stats_zero_division(self):
        """Test system stats with zero attempts"""
        mock_session = AsyncMock()

        mock_user = User(
            id=uuid4(),
            email="user@test.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        stats_data = {
            "total_attempts": 0,
            "total_questions": 0,
            "total_correct": 0,
            "last_attempt": None,
            "companies_count": 0
        }

        with patch.object(QuizAttemptRepository, 'get_user_system_stats', new_callable=AsyncMock) as mock_get_stats:
            mock_get_stats.return_value = stats_data

            service = QuizAttemptService(mock_session)
            result = await service.get_user_system_stats(mock_user)

            assert result.stats.average_score == 0.0
            assert result.companies_participated == 0
