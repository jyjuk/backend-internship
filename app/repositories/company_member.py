from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.company_member import CompanyMember
from app.repositories.base import BaseRepository


class CompanyMemberRepository(BaseRepository[CompanyMember]):
    """Repository for CompanyMember model"""

    def __init__(self, session: AsyncSession):
        super().__init__(CompanyMember, session)

    async def get_by_user_and_company(self, user_id: UUID, company_id: UUID) -> Optional[CompanyMember]:
        """Check if user is member of company"""
        result = await self.get_all(
            limit=1,
            filters={"user_id": user_id, "company_id": company_id}
        )
        return result[0] if result else None

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

    async def get_company_admins(self, company_id: UUID, skip: int = 0, limit: int = 100) -> List[CompanyMember]:
        """Get all admins of a company"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"company_id": company_id, "is_admin": True},
            order_by=CompanyMember.created_at.desc()
        )

    async def count_company_admins(self, company_id: UUID) -> int:
        """Count admins in company"""
        return await self.count(filters={"company_id": company_id, "is_admin": True})
