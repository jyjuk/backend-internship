from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import UUID
from enum import Enum
from typing import TYPE_CHECKING
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.company import Company


class RequestStatus(str, Enum):
    """Request status enum"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CANCELLED = "cancelled"


class CompanyRequest(Base, UUIDMixin, TimestampMixin):
    """Company membership request model"""

    __tablename__ = "company_requests"

    company_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default=RequestStatus.PENDING.value, nullable=False)
    company: Mapped["Company"] = relationship(back_populates="requests")
    user: Mapped["User"] = relationship(back_populates="company_requests")

    def __repr__(self) -> str:
        return f"<CompanyRequest(id={self.id}, company_id={self.company_id}, status={self.status})>"
