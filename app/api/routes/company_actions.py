from fastapi import APIRouter, Depends, status, Query
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.company_action import CompanyActionService
from app.schemas.company_action import (
    InvitationCreate,
    InvitationResponse,
    InvitationList,
    RequestResponse,
    RequestList,
    MemberList,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/companies", tags=["Company Actions"])


@router.post("/{company_id}/invitations", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
        company_id: UUID,
        data: InvitationCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Owner invites user to company"""
    service = CompanyActionService(db)
    return await service.create_invitation(company_id, data, current_user)


@router.delete("/{company_id}/invitations/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_invitation(
        company_id: UUID,
        invitation_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Owner cancels invitation"""
    service = CompanyActionService(db)
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
    service = CompanyActionService(db)
    return await service.get_company_invitations(company_id, current_user, skip, limit)


@router.get("/invitations/me", response_model=InvitationList)
async def get_my_invitations(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get user's received invitations"""
    service = CompanyActionService(db)
    return await service.get_user_invitations(current_user, skip, limit)


@router.post("/invitations/{invitation_id}/accept", status_code=status.HTTP_204_NO_CONTENT)
async def accept_invitation(
        invitation_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """User accepts invitation"""
    service = CompanyActionService(db)
    await service.accept_invitation(invitation_id, current_user)


@router.post("/invitations/{invitation_id}/decline", status_code=status.HTTP_204_NO_CONTENT)
async def decline_invitation(
        invitation_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """User declines invitation"""
    service = CompanyActionService(db)
    await service.decline_invitation(invitation_id, current_user)


@router.post("/{company_id}/requests", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
        company_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """User requests to join company"""
    service = CompanyActionService(db)
    return await service.create_request(company_id, current_user)


@router.delete("/{company_id}/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_request(
        company_id: UUID,
        request_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """User cancels their request"""
    service = CompanyActionService(db)
    await service.cancel_request(company_id, request_id, current_user)


@router.get("/requests/me", response_model=RequestList)
async def get_my_requests(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get user's membership requests"""
    service = CompanyActionService(db)
    return await service.get_user_requests(current_user, skip, limit)


@router.get("/{company_id}/requests", response_model=RequestList)
async def get_company_requests(
        company_id: UUID,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get pending requests for company (owner only)"""
    service = CompanyActionService(db)
    return await service.get_company_requests(company_id, current_user, skip, limit)


@router.post("/{company_id}/requests/{request_id}/accept", status_code=status.HTTP_204_NO_CONTENT)
async def accept_request(
        company_id: UUID,
        request_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Owner accepts request"""
    service = CompanyActionService(db)
    await service.accept_request(company_id, request_id, current_user)


@router.post("/{company_id}/requests/{request_id}/decline", status_code=status.HTTP_204_NO_CONTENT)
async def decline_request(
        company_id: UUID,
        request_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Owner declines request"""
    service = CompanyActionService(db)
    await service.decline_request(company_id, request_id, current_user)


@router.get("/{company_id}/members", response_model=MemberList)
async def get_company_members(
        company_id: UUID,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    """Get all members of company (public)"""
    service = CompanyActionService(db)
    return await service.get_company_members(company_id, skip, limit)


@router.delete("/{company_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
        company_id: UUID,
        user_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Owner removes member from company"""
    service = CompanyActionService(db)
    await service.remove_member(company_id, user_id, current_user)


@router.delete("/{company_id}/members/me", status_code=status.HTTP_204_NO_CONTENT)
async def leave_company(
        company_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """User leaves company"""
    service = CompanyActionService(db)
    await service.leave_company(company_id, current_user)
