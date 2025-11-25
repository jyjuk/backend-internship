from fastapi import APIRouter, Depends, status, Query
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.company_request_service import CompanyRequestService
from app.schemas.company_action import (
    RequestResponse,
    RequestList,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/companies", tags=["Company Requests"])


@router.post("/{company_id}/requests", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
        company_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """User requests to join company"""
    service = CompanyRequestService(db)
    return await service.create_request(company_id, current_user)


@router.delete("/{company_id}/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_request(
        company_id: UUID,
        request_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """User cancels their request"""
    service = CompanyRequestService(db)
    await service.cancel_request(company_id, request_id, current_user)


@router.get("/requests/me", response_model=RequestList)
async def get_my_requests(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get user's membership requests"""
    service = CompanyRequestService(db)
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
    service = CompanyRequestService(db)
    return await service.get_company_requests(company_id, current_user, skip, limit)


@router.post("/{company_id}/requests/{request_id}/accept", status_code=status.HTTP_204_NO_CONTENT)
async def accept_request(
        company_id: UUID,
        request_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Owner accepts request"""
    service = CompanyRequestService(db)
    await service.accept_request(company_id, request_id, current_user)


@router.post("/{company_id}/requests/{request_id}/decline", status_code=status.HTTP_204_NO_CONTENT)
async def decline_request(
        company_id: UUID,
        request_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Owner declines request"""
    service = CompanyRequestService(db)
    await service.decline_request(company_id, request_id, current_user)
