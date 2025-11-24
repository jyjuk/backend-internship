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
