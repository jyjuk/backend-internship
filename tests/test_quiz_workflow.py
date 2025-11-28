from app.services.quiz_attempt_service import QuizAttemptService
from app.repositories.quiz_attempt import QuizAttemptRepository


def test_quiz_attempt_service_has_required_methods():
    """Test that QuizAttemptService has all required methods"""
    assert hasattr(QuizAttemptService, 'submit_quiz')
    assert hasattr(QuizAttemptService, 'get_user_company_stats')
    assert hasattr(QuizAttemptService, 'get_user_system_stats')


def test_quiz_attempt_repository_has_required_methods():
    """Test that QuizAttemptRepository has all required methods"""
    assert hasattr(QuizAttemptRepository, 'get_user_attempts')
    assert hasattr(QuizAttemptRepository, 'get_user_company_attempts')
    assert hasattr(QuizAttemptRepository, 'get_last_attempt')
    assert hasattr(QuizAttemptRepository, 'get_user_company_stats')
    assert hasattr(QuizAttemptRepository, 'get_user_system_stats')


def test_quiz_submission_schema():
    """Test quiz submission schema structure"""
    from app.schemas.quiz import QuizSubmission, AnswerSubmission

    assert 'answers' in QuizSubmission.model_fields

    assert 'question_id' in AnswerSubmission.model_fields
    assert 'answer_ids' in AnswerSubmission.model_fields


def test_quiz_attempt_model_relationships():
    """Test that QuizAttempt has proper relationships"""
    from app.models.quiz_attempt import QuizAttempt

    assert hasattr(QuizAttempt, 'user')
    assert hasattr(QuizAttempt, 'quiz')
    assert hasattr(QuizAttempt, 'company')


def test_stats_schemas():
    """Test statistics schemas"""
    from app.schemas.quiz import UserQuizStats, UserCompanyStats, UserSystemStats

    assert 'total_attempts' in UserQuizStats.model_fields
    assert 'total_questions_answered' in UserQuizStats.model_fields
    assert 'total_correct_answers' in UserQuizStats.model_fields
    assert 'average_score' in UserQuizStats.model_fields
    assert 'last_attempt_at' in UserQuizStats.model_fields

    assert 'company_id' in UserCompanyStats.model_fields
    assert 'company_name' in UserCompanyStats.model_fields
    assert 'stats' in UserCompanyStats.model_fields

    assert 'stats' in UserSystemStats.model_fields
    assert 'companies_participated' in UserSystemStats.model_fields
