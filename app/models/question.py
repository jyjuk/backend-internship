from sqlalchemy import String, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import UUID
from typing import TYPE_CHECKING, List
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.quiz import Quiz
    from app.models.answer import Answer


class Question(Base, UUIDMixin, TimestampMixin):
    """Question model"""
    __tablename__ = "questions"

    quiz_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")
    answers: Mapped[List["Answer"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="Answer.order"
    )

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, quiz_id={self.quiz_id}, order={self.order})>"
