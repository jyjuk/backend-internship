import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.models.company_member import CompanyMember
from app.models.company_invitation import CompanyInvitation, InvitationStatus
from app.models.company_request import CompanyRequest, RequestStatus
from app.repositories.company import CompanyRepository
from app.repositories.company_member import CompanyMemberRepository
from app.repositories.company_invitation import CompanyInvitationRepository
from app.repositories.company_request import CompanyRequestRepository
from app.schemas.company_action import (
    InvitationCreate,
    InvitationResponse,
    InvitationList,
    RequestResponse,
    RequestList,
    MemberResponse,
    MemberList,
)

logger = logging.getLogger(__name__)


class CompanyActionService:
    """Service for company actions (invitations, requests, members)"""

    def __init__(self, session: AsyncSession):
        self.company_repo = CompanyRepository(session)
        self.member_repo = CompanyMemberRepository(session)
        self.invitation_repo = CompanyInvitationRepository(session)
        self.request_repo = CompanyRequestRepository(session)
        self.session = session

    async def _check_company_owner(self, company_id: UUID, user_id: UUID) -> None:
        """Check if user is company owner"""
        company = await self.company_repo.get_by_id(company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
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

    async def create_invitation(self, company_id: UUID, data: InvitationCreate, owner: User) -> InvitationResponse:
        """Owner invites user to company"""
        try:
            await self._check_company_owner(company_id, owner.id)
            await self._check_not_member(company_id, data.invited_user_id)

            existing = await self.invitation_repo.get_pending_invitation(company_id, data.invited_user_id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invitation already sent"
                )

            invitation = CompanyInvitation(
                company_id=company_id,
                invited_user_id=data.invited_user_id,
                invited_by_id=owner.id,
                status=InvitationStatus.PENDING.value
            )
            created = await self.invitation_repo.create(invitation)
            logger.info(f"Invitation created: {created.id} for user {data.invited_user_id} to company {company_id}")
            return InvitationResponse.model_validate(created)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating invitation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create invitation"
            )

    async def cancel_invitation(self, company_id: UUID, invitation_id: UUID, owner: User) -> None:
        """Owner cancels invitation"""
        try:
            await self._check_company_owner(company_id, owner.id)
            invitation = await self.invitation_repo.get_by_id(invitation_id)
            if not invitation or invitation.company_id != company_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invitation not found"
                )
            if invitation.status != InvitationStatus.PENDING.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only cancel pending invitations"
                )

            invitation.status = InvitationStatus.CANCELLED.value
            await self.invitation_repo.update(invitation)
            logger.info(f"Invitation cancelled: {invitation_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error cancelling invitation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel invitation"
            )

    async def get_company_invitations(
            self,
            company_id: UUID,
            owner: User,
            skip: int = 0,
            limit: int = 100
    ) -> InvitationList:
        """Get all invitations for company (owner only)"""
        try:
            await self._check_company_owner(company_id, owner.id)
            invitations = await self.invitation_repo.get_company_invitations(company_id, skip, limit)
            total = await self.invitation_repo.count_company_invitations(company_id)
            return InvitationList(
                invitations=[InvitationResponse.model_validate(inv) for inv in invitations],
                total=total
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting company invitations: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get invitations"
            )

    async def get_user_invitations(self, user: User, skip: int = 0, limit: int = 100) -> InvitationList:
        """Get user's received invitations"""
        try:
            invitations = await self.invitation_repo.get_user_invitations(user.id, skip, limit)
            total = await self.invitation_repo.count_user_invitations(user.id)
            return InvitationList(
                invitations=[InvitationResponse.model_validate(inv) for inv in invitations],
                total=total
            )
        except Exception as e:
            logger.error(f"Error getting user invitations: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get invitations"
            )

    async def accept_invitation(self, invitation_id: UUID, user: User) -> None:
        """User accepts invitation"""
        try:
            invitation = await self.invitation_repo.get_by_id(invitation_id)
            if not invitation or invitation.invited_user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invitation not found"
                )
            if invitation.status != InvitationStatus.PENDING.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invitation is not pending"
                )

            await self._check_not_member(invitation.company_id, user.id)

            member = CompanyMember(user_id=user.id, company_id=invitation.company_id)
            await self.member_repo.create(member)

            invitation.status = InvitationStatus.ACCEPTED.value
            await self.invitation_repo.update(invitation)
            logger.info(f"Invitation accepted: {invitation_id}, user {user.id} joined company {invitation.company_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error accepting invitation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to accept invitation"
            )

    async def decline_invitation(self, invitation_id: UUID, user: User) -> None:
        """User declines invitation"""
        try:
            invitation = await self.invitation_repo.get_by_id(invitation_id)
            if not invitation or invitation.invited_user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invitation not found"
                )
            if invitation.status != InvitationStatus.PENDING.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invitation is not pending"
                )

            invitation.status = InvitationStatus.DECLINED.value
            await self.invitation_repo.update(invitation)
            logger.info(f"Invitation declined: {invitation_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error declining invitation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to decline invitation"
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
                status=RequestStatus.PENDING.value
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
            if request.status != RequestStatus.PENDING.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only cancel pending requests"
                )

            request.status = RequestStatus.CANCELLED.value
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

    async def get_company_requests(self, company_id: UUID, owner: User, skip: int = 0, limit: int = 100) -> RequestList:
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
            if request.status != RequestStatus.PENDING.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request is not pending"
                )

            await self._check_not_member(company_id, request.user_id)

            member = CompanyMember(user_id=request.user_id, company_id=company_id)
            await self.member_repo.create(member)

            request.status = RequestStatus.ACCEPTED.value
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
            if request.status != RequestStatus.PENDING.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request is not pending"
                )

            request.status = RequestStatus.DECLINED.value
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

    async def get_company_members(self, company_id: UUID, skip: int = 0, limit: int = 100) -> MemberList:
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
