from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.company_member import CompanyMember
from app.repositories.base import BaseRepository


class CompanyMemberRepository(BaseRepository[CompanyMember]):
    """Repository for CompanyMember model"""

    def __init__(self, session: AsyncSession):
        super().__init__(CompanyMember, session)

    async def get_by_user_and_company(self, user_id: UUID, company_id: UUID) -> Optional[CompanyMember]:
        """Check if user is member of company"""
        result = await self.session.execute(
            select(CompanyMember).where(CompanyMember.user_id == user_id, CompanyMember.company_id == company_id)
        )
        return result.scalar_one_or_none()

    async def get_company_members(self, company_id: UUID, skip: int = 0, limit: int = 100) -> List[CompanyMember]:
        """Get all members of a company"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"company_id": company_id},
            order_by=CompanyMember.created_at.desc()
        )

    async def count_company_members(self, company_id: UUID) -> int:
        """Count members in company"""
        return await self.count(filters={"company_id": company_id})
