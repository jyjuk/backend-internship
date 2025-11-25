from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.company_invitation import CompanyInvitation, InvitationStatus
from app.repositories.base import BaseRepository


class CompanyInvitationRepository(BaseRepository[CompanyInvitation]):
    """Repository for CompanyInvitation model"""

    def __init__(self, session: AsyncSession):
        super().__init__(CompanyInvitation, session)

    async def get_pending_invitation(self, company_id: UUID, user_id: UUID) -> Optional[CompanyInvitation]:
        """Get pending invitation for user to company"""
        result = await self.get_all(
            limit=1,
            filters={
                "company_id": company_id,
                "invited_user_id": user_id,
                "status": InvitationStatus.PENDING
            }
        )
        return result[0] if result else None

    async def get_company_invitations(
            self,
            company_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> List[CompanyInvitation]:
        """Get all invitations for company"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"company_id": company_id},
            order_by=CompanyInvitation.created_at.desc()
        )

    async def get_user_invitations(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[CompanyInvitation]:
        """Get all invitations received by user"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={
                "invited_user_id": user_id,
                "status": InvitationStatus.PENDING
            },
            order_by=CompanyInvitation.created_at.desc()
        )

    async def count_company_invitations(self, company_id: UUID) -> int:
        """Count invitations for company"""
        return await self.count(filters={"company_id": company_id})

    async def count_user_invitations(self, user_id: UUID) -> int:
        """Count pending invitations for user"""
        return await self.count(filters={"invited_user_id": user_id, "status": InvitationStatus.PENDING})
