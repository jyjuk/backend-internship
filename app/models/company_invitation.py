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


class InvitationStatus(str, Enum):
    """Invitation status enum"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CANCELLED = "cancelled"


class CompanyInvitation(Base, UUIDMixin, TimestampMixin):
    """Company invitation model"""
    __tablename__ = "company_invitations"

    company_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )
    invited_user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    invited_by_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default=InvitationStatus.PENDING.value, nullable=False)

    company: Mapped["Company"] = relationship(back_populates="invitations")
    invited_user: Mapped["User"] = relationship(foreign_keys=[invited_user_id], back_populates="received_invitations")
    invited_by: Mapped["User"] = relationship(foreign_keys=[invited_by_id], back_populates="sent_invitations")

    def __repr__(self) -> str:
        return f"<CompanyInvitation(id={self.id}, company_id={self.company_id}, status={self.status})>"
