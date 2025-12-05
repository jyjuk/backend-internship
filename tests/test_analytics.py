from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import WeeklyTrend


def test_analytics_service_has_required_methods():
    """Test that AnalyticsService has all required methods"""
    assert hasattr(AnalyticsService, 'get_user_overall_analytics')
    assert hasattr(AnalyticsService, 'get_user_quiz_analytics')
    assert hasattr(AnalyticsService, 'get_user_recent_attempts')
    assert hasattr(AnalyticsService, 'get_company_overview_analytics')
    assert hasattr(AnalyticsService, 'get_company_members_analytics')
    assert hasattr(AnalyticsService, 'get_company_quizzes_analytics')
    assert hasattr(AnalyticsService, 'get_user_in_company_analytics')
    assert hasattr(AnalyticsService, '_check_owner_or_admin')
    assert hasattr(AnalyticsService, '_get_week_number')
    assert hasattr(AnalyticsService, '_calculate_weekly_trends')


def test_week_number_format():
    """Test ISO week number formatting"""
    from datetime import datetime

    date = datetime(2024, 12, 3)
    week = AnalyticsService._get_week_number(date)

    assert isinstance(week, str)
    assert week.startswith("2024-W")
    assert len(week) == 8
    assert "-W" in week


def test_analytics_schemas():
    """Test that analytics schemas have required fields"""
    from app.schemas.analytics import (
        UserOverallAnalytics,
        QuizAnalytics,
        CompanyOverviewAnalytics,
        MemberAnalytics
    )

    assert 'average_score' in UserOverallAnalytics.model_fields
    assert 'total_attempts' in UserOverallAnalytics.model_fields
    assert 'total_companies' in UserOverallAnalytics.model_fields
    assert 'total_quizzes_taken' in UserOverallAnalytics.model_fields

    assert 'quiz_id' in QuizAnalytics.model_fields
    assert 'quiz_title' in QuizAnalytics.model_fields
    assert 'average_score' in QuizAnalytics.model_fields
    assert 'weekly_trend' in QuizAnalytics.model_fields

    assert 'company_id' in CompanyOverviewAnalytics.model_fields
    assert 'total_members' in CompanyOverviewAnalytics.model_fields
    assert 'average_company_score' in CompanyOverviewAnalytics.model_fields
    assert 'weekly_trend' in CompanyOverviewAnalytics.model_fields

    assert 'user_id' in MemberAnalytics.model_fields
    assert 'username' in MemberAnalytics.model_fields
    assert 'average_score' in MemberAnalytics.model_fields
    assert 'last_attempt_at' in MemberAnalytics.model_fields


def test_weekly_trend_schema():
    """Test WeeklyTrend schema"""
    trend = WeeklyTrend(
        week="2024-W49",
        avg_score=85.5,
        attempts=10
    )

    assert trend.week == "2024-W49"
    assert trend.avg_score == 85.5
    assert trend.attempts == 10
