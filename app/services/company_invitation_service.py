import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.models.company_member import CompanyMember
from app.models.company_invitation import CompanyInvitation, InvitationStatus
from app.repositories.company import CompanyRepository
from app.repositories.company_member import CompanyMemberRepository
from app.repositories.company_invitation import CompanyInvitationRepository
from app.schemas.company_action import (
    InvitationCreate,
    InvitationResponse,
    InvitationList,
)

logger = logging.getLogger(__name__)


class CompanyInvitationService:
    """Service for company invitations"""

    def __init__(self, session: AsyncSession):
        self.company_repo = CompanyRepository(session)
        self.member_repo = CompanyMemberRepository(session)
        self.invitation_repo = CompanyInvitationRepository(session)
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
                status=InvitationStatus.PENDING
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
            if invitation.status != InvitationStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only cancel pending invitations"
                )

            invitation.status = InvitationStatus.CANCELLED
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
            if invitation.status != InvitationStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invitation is not pending"
                )

            await self._check_not_member(invitation.company_id, user.id)

            member = CompanyMember(user_id=user.id, company_id=invitation.company_id)
            await self.member_repo.create(member)

            invitation.status = InvitationStatus.ACCEPTED
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
            if invitation.status != InvitationStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invitation is not pending"
                )

            invitation.status = InvitationStatus.DECLINED
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
