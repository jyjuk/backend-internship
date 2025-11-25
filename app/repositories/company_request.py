from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.company_request import CompanyRequest, RequestStatus
from app.repositories.base import BaseRepository


class CompanyRequestRepository(BaseRepository[CompanyRequest]):
    """Repository for CompanyRequest model"""

    def __init__(self, session: AsyncSession):
        super().__init__(CompanyRequest, session)

    async def get_pending_request(self, company_id: UUID, user_id: UUID) -> Optional[CompanyRequest]:
        """Get pending request from user to company"""
        result = await self.get_all(
            limit=1,
            filters={
                "company_id": company_id,
                "user_id": user_id,
                "status": RequestStatus.PENDING
            }
        )
        return result[0] if result else None

    async def get_company_requests(self, company_id: UUID, skip: int = 0, limit: int = 100) -> List[CompanyRequest]:
        """Get all requests for company"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={
                "company_id": company_id,
                "status": RequestStatus.PENDING
            },
            order_by=CompanyRequest.created_at.desc()
        )

    async def get_user_requests(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[CompanyRequest]:
        """Get all request made by user"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"user_id": user_id},
            order_by=CompanyRequest.created_at.desc()
        )

    async def count_company_requests(self, company_id: UUID) -> int:
        """Count pending request for company"""
        return await self.count(filters={"company_id": company_id, "status": RequestStatus.PENDING.value})

    async def count_user_requests(self, user_id: UUID) -> int:
        """Count request made by user"""
        return await self.count(filters={"user_id": user_id})
