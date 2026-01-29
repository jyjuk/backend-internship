import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.models.company_member import CompanyMember
from app.models.company_request import CompanyRequest, RequestStatus
from app.repositories.company import CompanyRepository
from app.repositories.company_member import CompanyMemberRepository
from app.repositories.company_request import CompanyRequestRepository
from app.schemas.company_action import (
    RequestResponse,
    RequestList,
)

logger = logging.getLogger(__name__)


class CompanyRequestService:
    """Service for company membership requests"""

    def __init__(self, session: AsyncSession):
        self.company_repo = CompanyRepository(session)
        self.member_repo = CompanyMemberRepository(session)
        self.request_repo = CompanyRequestRepository(session)
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

    async def _check_not_member(self, company_id: UUID, user_id: UUID) -> None:
        """Check user is not already a member"""
        member = await self.member_repo.get_by_user_and_company(user_id, company_id)
        if member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member"
            )

    async def create_request(self, company_id: UUID, user: User) -> RequestResponse:
        """User requests to join company"""
        try:
            company = await self.company_repo.get_by_id(company_id)
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )

            await self._check_not_member(company_id, user.id)

            existing = await self.request_repo.get_pending_request(company_id, user.id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request already sent"
                )

            request = CompanyRequest(
                company_id=company_id,
                user_id=user.id,
                status=RequestStatus.PENDING
            )
            created = await self.request_repo.create(request)
            logger.info(f"Request created: {created.id} from user {user.id} to company {company_id}")
            return RequestResponse.model_validate(created)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating request: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create request"
            )

    async def cancel_request(self, company_id: UUID, request_id: UUID, user: User) -> None:
        """User cancels their request"""
        try:
            request = await self.request_repo.get_by_id(request_id)
            if not request or request.user_id != user.id or request.company_id != company_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Request not found"
                )
            if request.status != RequestStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only cancel pending requests"
                )

            request.status = RequestStatus.CANCELLED
            await self.request_repo.update(request)
            logger.info(f"Request cancelled: {request_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error cancelling request: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel request"
            )

    async def get_company_requests(
            self,
            company_id: UUID,
            owner: User,
            skip: int = 0,
            limit: int = 100
    ) -> RequestList:
        """Get pending requests for company (owner only)"""
        try:
            await self._check_company_owner(company_id, owner.id)
            requests = await self.request_repo.get_company_requests(company_id, skip, limit)
            total = await self.request_repo.count_company_requests(company_id)
            return RequestList(
                requests=[RequestResponse.model_validate(req) for req in requests],
                total=total
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting company requests: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get requests"
            )

    async def get_user_requests(self, user: User, skip: int = 0, limit: int = 100) -> RequestList:
        """Get user's membership requests"""
        try:
            requests = await self.request_repo.get_user_requests(user.id, skip, limit)
            total = await self.request_repo.count_user_requests(user.id)
            return RequestList(
                requests=[RequestResponse.model_validate(req) for req in requests],
                total=total
            )
        except Exception as e:
            logger.error(f"Error getting user requests: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get requests"
            )

    async def accept_request(self, company_id: UUID, request_id: UUID, owner: User) -> None:
        """Owner accepts request"""
        try:
            await self._check_company_owner(company_id, owner.id)
            request = await self.request_repo.get_by_id(request_id)
            if not request or request.company_id != company_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Request not found"
                )
            if request.status != RequestStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request is not pending"
                )

            await self._check_not_member(company_id, request.user_id)

            member = CompanyMember(user_id=request.user_id, company_id=company_id)
            await self.member_repo.create(member)

            request.status = RequestStatus.ACCEPTED
            await self.request_repo.update(request)
            logger.info(f"Request accepted: {request_id}, user {request.user_id} joined company {company_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error accepting request: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to accept request"
            )

    async def decline_request(self, company_id: UUID, request_id: UUID, owner: User) -> None:
        """Owner declines request"""
        try:
            await self._check_company_owner(company_id, owner.id)
            request = await self.request_repo.get_by_id(request_id)
            if not request or request.company_id != company_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Request not found"
                )
            if request.status != RequestStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request is not pending"
                )

            request.status = RequestStatus.DECLINED
            await self.request_repo.update(request)
            logger.info(f"Request declined: {request_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error declining request: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to decline request"
            )
