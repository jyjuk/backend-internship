from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List


class WeeklyTrend(BaseModel):
    """Weekly score trend"""
    week: str
    avg_score: float
    attempts: int


class UserOverallAnalytics(BaseModel):
    """User overall analytics across all companies"""
    average_score: float
    total_attempts: int
    total_companies: int
    total_quizzes_taken: int


class QuizAnalytics(BaseModel):
    """Analytics for a specific quiz"""
    quiz_id: UUID
    quiz_title: str
    company_id: UUID
    company_name: str
    average_score: float
    attempts_count: int
    last_attempt_at: datetime | None
    weekly_trend: List[WeeklyTrend]


class UserQuizAnalyticsList(BaseModel):
    """List of user`s quiz analytics"""
    quizzes: List[QuizAnalytics]


class RecentAttempt(BaseModel):
    """Recent quiz attempt"""
    quiz_id: UUID
    quiz_title: str
    company_name: str
    score: int
    total_questions: int
    percentage: float
    completed_at: datetime


class RecentAttemptsList(BaseModel):
    """List of recent attempts"""
    attempts: List[RecentAttempt]


class CompanyOverviewAnalytics(BaseModel):
    """Company analytics overview"""
    company_id: UUID
    company_name: str
    total_members: int
    total_quizzes: int
    total_attempts: int
    average_company_score: float
    weekly_trend: List[WeeklyTrend]


class MemberAnalytics(BaseModel):
    """Analytics for a company member"""
    user_id: UUID
    username: str
    email: str
    total_attempts: int
    average_score: float
    last_attempt_at: datetime | None


class CompanyMemberAnalyticsList(BaseModel):
    """Company member analytics list"""
    members: List[MemberAnalytics]


class CompanyQuizAnalytics(BaseModel):
    """Analytics for company quiz"""
    quiz_id: UUID
    quiz_title: str
    total_attempts: int
    average_score: float
    completion_rate: float
    weekly_trend: List[WeeklyTrend]


class CompanyQuizzesAnalytics(BaseModel):
    """Company quizzes analytics list"""
    quizzes: List[CompanyQuizAnalytics]


class UserInCompanyAnalytics(BaseModel):
    """Detailed analytics for user in specific company"""
    user_id: UUID
    username: str
    company_id: UUID
    company_name: str
    total_attempts: int
    average_score: float
    quizzes: List[QuizAnalytics]
