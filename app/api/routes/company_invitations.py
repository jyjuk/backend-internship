from fastapi import APIRouter, Depends, status, Query
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.company_invitation_service import CompanyInvitationService
from app.schemas.company_action import (
    InvitationCreate,
    InvitationResponse,
    InvitationList,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/companies", tags=["Company Invitations"])


@router.post("/{company_id}/invitations", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
        company_id: UUID,
        data: InvitationCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Owner invites user to company"""
    service = CompanyInvitationService(db)
    return await service.create_invitation(company_id, data, current_user)


@router.delete("/{company_id}/invitations/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_invitation(
        company_id: UUID,
        invitation_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Owner cancels invitation"""
    service = CompanyInvitationService(db)
    await service.cancel_invitation(company_id, invitation_id, current_user)


@router.get("/{company_id}/invitations", response_model=InvitationList)
async def get_company_invitations(
        company_id: UUID,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get all invitations for company (owner only)"""
    service = CompanyInvitationService(db)
    return await service.get_company_invitations(company_id, current_user, skip, limit)


@router.get("/invitations/me", response_model=InvitationList)
async def get_my_invitations(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get user's received invitations"""
    service = CompanyInvitationService(db)
    return await service.get_user_invitations(current_user, skip, limit)


@router.post("/invitations/{invitation_id}/accept", status_code=status.HTTP_204_NO_CONTENT)
async def accept_invitation(
        invitation_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """User accepts invitation"""
    service = CompanyInvitationService(db)
    await service.accept_invitation(invitation_id, current_user)


@router.post("/invitations/{invitation_id}/decline", status_code=status.HTTP_204_NO_CONTENT)
async def decline_invitation(
        invitation_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """User declines invitation"""
    service = CompanyInvitationService(db)
    await service.decline_invitation(invitation_id, current_user)
