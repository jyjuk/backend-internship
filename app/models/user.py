from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.company_member import CompanyMember
    from app.models.company_invitation import CompanyInvitation
    from app.models.company_request import CompanyRequest
    from app.models.quiz_attempt import QuizAttempt
    from app.models.notification import Notification


class User(Base, UUIDMixin, TimestampMixin):
    """User model"""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    companies: Mapped[List["Company"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    memberships: Mapped[List["CompanyMember"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    received_invitations: Mapped[List["CompanyInvitation"]] = relationship(
        foreign_keys="CompanyInvitation.invited_user_id",
        back_populates="invited_user",
        cascade="all, delete-orphan"
    )
    sent_invitations: Mapped[List["CompanyInvitation"]] = relationship(
        foreign_keys="CompanyInvitation.invited_by_id",
        back_populates="invited_by",
        cascade="all, delete-orphan"
    )
    company_requests: Mapped[List["CompanyRequest"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    quiz_attempts: Mapped[List["QuizAttempt"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
