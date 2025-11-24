from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.company import Company
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """Repository for Company model"""

    def __init__(self, session: AsyncSession):
        super().__init__(Company, session)

    async def get_all(self, skip: int = 0, limit: int = 100, visible_only: bool = True) -> List[Company]:
        """Get all companies with pagination"""
        query = select(Company)
        if visible_only:
            query = query.where(Company.is_visible == True)
        query = query.offset(skip).limit(limit).order_by(Company.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self, visible_only: bool = True) -> int:
        """Count total companies"""
        query = select(func.count(Company.id))
        if visible_only:
            query = query.where(Company.is_visible == True)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_by_owner(self, owner_id: UUID, skip: int = 0, limit: int = 100) -> List[Company]:
        """Get all companies owned by user"""
        result = await self.session.execute(
            select(Company).where(Company.owner_id == owner_id).offset(skip).limit(limit).order_by(
                Company.created_at.desc())
        )
        return list(result.scalars().all())
