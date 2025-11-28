from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID
from datetime import datetime
from typing import List


class AnswerCreate(BaseModel):
    """Schema for creating answer"""
    text: str = Field(..., min_length=1, max_length=500, description="Answer text")
    is_correct: bool = Field(..., description="Is this answer correct")
    order: int = Field(..., ge=0, description="Answer order")


class AnswerResponse(BaseModel):
    """Answer response schema"""
    id: UUID
    question_id: UUID
    text: str
    is_correct: bool
    order: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(BaseModel):
    """Schema for creating question"""
    title: str = Field(..., min_length=1, max_length=1000, description="Question title")
    order: int = Field(..., ge=0, description="Question order")
    answers: List[AnswerCreate] = Field(..., min_length=2, max_length=4, description="List of answers (2-4)")

    @field_validator("answers")
    @classmethod
    def validate_answer(cls, answers: List[AnswerCreate]) -> List[AnswerCreate]:
        """Validate that at least one answer is correct"""
        if not any(answer.is_correct for answer in answers):
            raise ValueError("at least one answer must be correct")
        return answers


class QuestionResponse(BaseModel):
    """Question response schema"""
    id: UUID
    quiz_id: UUID
    title: str
    order: int
    answers: List[AnswerResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizCreate(BaseModel):
    """Schema for creating quiz"""
    title: str = Field(..., min_length=1, max_length=255, description="Quiz title")
    description: str | None = Field(None, max_length=2000, description="Quiz description")
    questions: List[QuestionCreate] = Field(..., min_length=2, description="list of questions")


class QuizUpdate(BaseModel):
    """Schema for updating quiz"""
    title: str | None = Field(None, min_length=1, max_length=255, description="Quiz title")
    description: str | None = Field(None, max_length=2000, description="Quiz description")
    questions: List[QuestionCreate] | None = Field(None, min_length=2, description="List of questions (min 2)")

    @field_validator("questions")
    @classmethod
    def validate_questions(cls, questions: List[QuestionCreate] | None) -> List[QuestionCreate] | None:
        """Validate questions if provided"""
        if questions is not None and len(questions) < 2:
            raise ValueError("Quiz must have at least 2 questions")
        return questions


class QuizResponse(BaseModel):
    """Quiz response schema"""
    id: UUID
    company_id: UUID
    title: str
    description: str | None
    frequency: int
    questions: List[QuestionResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizList(BaseModel):
    """List of quizzes"""
    quizzes: List[QuizResponse]
    total: int
