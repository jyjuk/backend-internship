from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.company import Company
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """Repository for Company model"""

    def __init__(self, session: AsyncSession):
        super().__init__(Company, session)

    async def get_all_visible(self, skip: int = 0, limit: int = 100) -> List[Company]:
        """Get companies with pagination"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"is_visible": True},
            order_by=Company.created_at.desc()
        )

    async def count_visible(self) -> int:
        """Count total companies"""
        return await self.count(filters={"is_visible": True})

    async def get_by_owner(self, owner_id: UUID, skip: int = 0, limit: int = 100) -> List[Company]:
        """Get all companies owned by user"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"owner_id": owner_id},
            order_by=Company.created_at.desc()
        )

    async def get_user_all_companies(
            self,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> List[Company]:
        """Get ALL companies where user is owner OR member (includes private)"""
        from app.models.company_member import CompanyMember

        stmt = select(Company).outerjoin(
            CompanyMember,
            Company.id == CompanyMember.company_id
        ).where(
            or_(
                Company.owner_id == user_id,
                CompanyMember.user_id == user_id
            )
        ).distinct().order_by(
            Company.created_at.desc()
        ).offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def count_user_all_companies(self, user_id: UUID) -> int:
        """Count ALL companies where user is owner OR member"""
        from app.models.company_member import CompanyMember

        stmt = select(func.count(Company.id.distinct())).outerjoin(
            CompanyMember,
            Company.id == CompanyMember.company_id
        ).where(
            or_(
                Company.owner_id == user_id,
                CompanyMember.user_id == user_id
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_user_public_companies(
            self,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> List[Company]:
        """Get ONLY PUBLIC companies where user is owner OR member"""
        from app.models.company_member import CompanyMember

        stmt = select(Company).outerjoin(
            CompanyMember,
            Company.id == CompanyMember.company_id
        ).where(
            and_(
                or_(
                    Company.owner_id == user_id,
                    CompanyMember.user_id == user_id
                ),
                Company.is_visible == True
            )
        ).distinct().order_by(
            Company.created_at.desc()
        ).offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def count_user_public_companies(self, user_id: UUID) -> int:
        """Count ONLY PUBLIC companies where user is owner OR member"""
        from app.models.company_member import CompanyMember

        stmt = select(func.count(Company.id.distinct())).outerjoin(
            CompanyMember,
            Company.id == CompanyMember.company_id
        ).where(
            and_(
                or_(
                    Company.owner_id == user_id,
                    CompanyMember.user_id == user_id
                ),
                Company.is_visible == True
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar() or 0
