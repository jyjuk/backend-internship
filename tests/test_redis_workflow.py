from app.services.redis_service import RedisService


def test_redis_service_has_required_methods():
    """Test that RedisService has all required methods"""
    assert hasattr(RedisService, 'store_quiz_response')
    assert hasattr(RedisService, 'get_question_response')
    assert hasattr(RedisService, 'get_user_quiz_responses')
    assert hasattr(RedisService, 'delete_quiz_responses')
    assert hasattr(RedisService, '_make_key')
    assert hasattr(RedisService, '_make_pattern')


def test_redis_service_constants():
    """Test that RedisService has correct constants"""
    assert RedisService.RESPONSE_TTL == 172800  # 48 hours
    assert RedisService.KEY_PREFIX == "quiz_response"


def test_redis_key_format():
    """Test Redis key generation"""
    from uuid import UUID

    user_id = UUID('12345678-1234-5678-1234-567812345678')
    quiz_id = UUID('87654321-4321-8765-4321-876543218765')
    question_id = UUID('11111111-2222-3333-4444-555555555555')

    key = RedisService._make_key(user_id, quiz_id, question_id)

    assert key.startswith(RedisService.KEY_PREFIX)
    assert str(user_id) in key
    assert str(quiz_id) in key
    assert str(question_id) in key
    assert key.count(':') == 3


def test_redis_pattern_format():
    """Test Redis pattern generation"""
    from uuid import UUID

    user_id = UUID('12345678-1234-5678-1234-567812345678')
    quiz_id = UUID('87654321-4321-8765-4321-876543218765')

    pattern = RedisService._make_pattern(user_id, quiz_id)

    assert pattern.startswith(RedisService.KEY_PREFIX)
    assert str(user_id) in pattern
    assert str(quiz_id) in pattern
    assert pattern.endswith('*')


def test_quiz_response_schemas():
    """Test quiz response schemas"""
    from app.schemas.quiz import QuizResponseDetail, QuizResponsesList

    assert 'user_id' in QuizResponseDetail.model_fields
    assert 'company_id' in QuizResponseDetail.model_fields
    assert 'quiz_id' in QuizResponseDetail.model_fields
    assert 'question_id' in QuizResponseDetail.model_fields
    assert 'answer_ids' in QuizResponseDetail.model_fields
    assert 'is_correct' in QuizResponseDetail.model_fields
    assert 'answered_at' in QuizResponseDetail.model_fields

    assert 'responses' in QuizResponsesList.model_fields
    assert 'total' in QuizResponsesList.model_fields

    assert hasattr(QuizResponseDetail, 'from_redis')
