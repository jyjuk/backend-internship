from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import UUID
from typing import TYPE_CHECKING
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.quiz import Quiz
    from app.models.company import Company


class QuizAttempt(Base, UUIDMixin, TimestampMixin):
    """Quiz attempt model"""
    __tablename__ = "quiz_attempts"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    quiz_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False
    )
    company_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )

    score: Mapped[int] = mapped_column(Integer, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="quiz_attempts")
    quiz: Mapped["Quiz"] = relationship(back_populates="attempts")
    company: Mapped["Company"] = relationship(back_populates="quiz_attempts")

    def __repr__(self) -> str:
        return f"<QuizAttempts(" \
               f"id={self.id}, " \
               f"user_id={self.user_id}, " \
               f"quiz_id={self.quiz_id}, " \
               f"score={self.score}/{self.total_questions}" \
               f")>"
