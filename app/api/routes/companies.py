import logging
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.company import CompanyService
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyDetail,
    CompanyList
)
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companies", tags=["companies"])


def get_company_service(db: AsyncSession = Depends(get_db)) -> CompanyService:
    return CompanyService(db)


@router.post("/", response_model=CompanyDetail, status_code=status.HTTP_201_CREATED)
async def create_company(
        data: CompanyCreate,
        current_user: User = Depends(get_current_user),
        service: CompanyService = Depends(get_company_service)
):
    """Create a new company"""
    return await service.create_company(data, current_user)


@router.get("/", response_model=CompanyList)
async def get_companies(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
        service: CompanyService = Depends(get_company_service),
):
    """Get all visible companies"""
    return await service.get_all_companies(skip=skip, limit=limit)


@router.get("/{company_id}", response_model=CompanyDetail)
async def get_company(
        company_id: UUID,
        service: CompanyService = Depends(get_company_service),
):
    """Get company by ID"""
    return await service.get_company_by_id(company_id)


@router.put("/{company_id}", response_model=CompanyDetail)
async def update_company(
        company_id: UUID,
        data: CompanyUpdate,
        current_user: User = Depends(get_current_user),
        service: CompanyService = Depends(get_company_service),
):
    """Update company"""
    return await service.update_company(company_id, data, current_user)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
        company_id: UUID,
        current_user: User = Depends(get_current_user),
        service: CompanyService = Depends(get_company_service),
):
    """Delete company (only owner)"""
    await service.delete_company(company_id, current_user)
