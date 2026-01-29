from app.services.export_service import ExportService


def test_export_service_has_required_methods():
    """Test that ExportService has all required methods"""
    assert hasattr(ExportService, 'export_user_responses')
    assert hasattr(ExportService, 'export_company_user_responses')
    assert hasattr(ExportService, 'export_quiz_responses')
    assert hasattr(ExportService, '_check_owner_or_admin')
    assert hasattr(ExportService, '_response_to_json')
    assert hasattr(ExportService, '_response_to_csv')


def test_json_conversion():
    """Test JSON conversion from responses"""
    import json

    responses = [
        {
            "user_id": "test-uuid",
            "quiz_id": "quiz-uuid",
            "is_correct": True
        }
    ]

    result = ExportService._response_to_json(responses)

    parsed = json.loads(result)
    assert len(parsed) == 1
    assert parsed[0]["is_correct"] is True


def test_csv_conversion():
    """Test CSV conversion from responses"""
    responses = [
        {
            "user_id": "user-1",
            "company_id": "company-1",
            "quiz_id": "quiz-1",
            "question_id": "question-1",
            "answer_ids": ["answer-1", "answer-2"],
            "is_correct": True,
            "answered_at": "2024-01-15T10:30:00Z"
        }
    ]

    result = ExportService._response_to_csv(responses)

    lines = result.strip().split('\n')
    assert len(lines) == 2
    assert "user_id" in lines[0]
    assert "is_correct" in lines[0]
    assert "user-1" in lines[1]


def test_csv_empty_responses():
    """Test CSV conversion with empty responses"""
    result = ExportService._response_to_csv([])
    assert result == ""


def test_csv_answer_ids_formatting():
    """Test that answer_ids are properly formatted as JSON array in CSV"""
    import json

    responses = [
        {
            "user_id": "user-1",
            "company_id": "company-1",
            "quiz_id": "quiz-1",
            "question_id": "question-1",
            "answer_ids": ["answer-1", "answer-2"],
            "is_correct": True,
            "answered_at": "2024-01-15T10:30:00Z"
        }
    ]

    result = ExportService._response_to_csv(responses)
    lines = result.strip().split('\n')

    assert '"answer-1"' in lines[1] or "'answer-1'" in lines[1]
