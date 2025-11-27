from app.services.quiz_service import QuizService
from app.repositories.quiz import QuizRepository
from app.repositories.question import QuestionRepository
from app.repositories.answer import AnswerRepository


def test_quiz_service_has_required_methods():
    """Test that QuizService has all required methods"""
    assert hasattr(QuizService, 'create_quiz')
    assert hasattr(QuizService, 'update_quiz')
    assert hasattr(QuizService, 'delete_quiz')
    assert hasattr(QuizService, 'get_company_quizzes')
    assert hasattr(QuizService, 'get_quiz')
    assert hasattr(QuizService, '_check_owner_or_admin')


def test_quiz_repository_has_required_methods():
    """Test that QuizRepository has all required methods"""
    assert hasattr(QuizRepository, 'get_company_quizzes')
    assert hasattr(QuizRepository, 'count_company_quizzes')
    assert hasattr(QuizRepository, 'get_quiz_with_questions')


def test_question_repository_exists():
    """Test that QuestionRepository exists"""
    assert QuestionRepository is not None


def test_answer_repository_exists():
    """Test that AnswerRepository exists"""
    assert AnswerRepository is not None


def test_quiz_schema_validation():
    """Test that Quiz schemas have proper validation"""
    from app.schemas.quiz import QuizCreate, QuestionCreate, AnswerCreate

    assert QuizCreate.model_fields['questions'].metadata

    assert QuestionCreate.model_fields['answers'].metadata

    assert 'text' in AnswerCreate.model_fields
    assert 'is_correct' in AnswerCreate.model_fields
    assert 'order' in AnswerCreate.model_fields


def test_quiz_models_relationships():
    """Test that Quiz models have proper relationships"""
    from app.models.quiz import Quiz
    from app.models.question import Question
    from app.models.answer import Answer

    assert hasattr(Quiz, 'questions')

    assert hasattr(Question, 'quiz')
    assert hasattr(Question, 'answers')

    assert hasattr(Answer, 'question')
