from fastapi import APIRouter, Depends, status, Query
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.company_member_service import CompanyMemberService
from app.schemas.company_action import MemberList
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/companies", tags=["Company Members"])


@router.get("/{company_id}/members", response_model=MemberList)
async def get_company_members(
        company_id: UUID,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    """Get all members of company (public)"""
    service = CompanyMemberService(db)
    return await service.get_company_members(company_id, skip, limit)


@router.delete("/{company_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
        company_id: UUID,
        user_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Owner removes member from company"""
    service = CompanyMemberService(db)
    await service.remove_member(company_id, user_id, current_user)


@router.delete("/{company_id}/members/me", status_code=status.HTTP_204_NO_CONTENT)
async def leave_company(
        company_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """User leaves company"""
    service = CompanyMemberService(db)
    await service.leave_company(company_id, current_user)
