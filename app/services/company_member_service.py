import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.repositories.company import CompanyRepository
from app.repositories.company_member import CompanyMemberRepository
from app.schemas.company_action import (
    MemberList,
    MemberResponse,
)

logger = logging.getLogger(__name__)


class CompanyMemberService:
    """Service for company members management"""

    def __init__(self, session: AsyncSession):
        self.company_repo = CompanyRepository(session)
        self.member_repo = CompanyMemberRepository(session)
        self.session = session

    async def _check_company_owner(self, company_id: UUID, user_id: UUID) -> None:
        """Check if user is company owner"""
        company = await self.company_repo.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        if company.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only company owner can perform this action"
            )

    async def get_company_members(
            self,
            company_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> MemberList:
        """Get all members of company (public)"""
        try:
            company = await self.company_repo.get_by_id(company_id)
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )

            members = await self.member_repo.get_company_members(company_id, skip, limit)
            total = await self.member_repo.count_company_members(company_id)
            return MemberList(
                members=[MemberResponse.model_validate(m) for m in members],
                total=total
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting company members: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get members"
            )

    async def remove_member(self, company_id: UUID, user_id: UUID, owner: User) -> None:
        """Owner removes member from company"""
        try:
            await self._check_company_owner(company_id, owner.id)
            member = await self.member_repo.get_by_user_and_company(user_id, company_id)
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Member not found"
                )

            await self.member_repo.delete(member)
            logger.info(f"Member removed: user {user_id} from company {company_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing member: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove member"
            )

    async def leave_company(self, company_id: UUID, user: User) -> None:
        """User leaves company"""
        try:
            member = await self.member_repo.get_by_user_and_company(user.id, company_id)
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="You are not a member of this company"
                )

            await self.member_repo.delete(member)
            logger.info(f"User {user.id} left company {company_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error leaving company: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to leave company"
            )
