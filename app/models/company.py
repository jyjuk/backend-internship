from sqlalchemy import String, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import UUID
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.company_member import CompanyMember
    from app.models.company_invitation import CompanyInvitation
    from app.models.company_request import CompanyRequest
    from app.models.quiz import Quiz


class Company(Base, UUIDMixin, TimestampMixin):
    """Company model"""
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    owner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    owner: Mapped["User"] = relationship(back_populates="companies")
    members: Mapped[List["CompanyMember"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    invitations: Mapped[List["CompanyInvitation"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan"
    )
    requests: Mapped[List["CompanyRequest"]] = relationship(back_populates="company", cascade="all, delete-orphan")

    quizzes: Mapped[List["Quiz"]] = relationship(back_populates="company", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name={self.name}, owner_id={self.owner_id}>"
