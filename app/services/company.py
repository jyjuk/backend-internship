import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.company import Company
from app.models.user import User
from app.repositories.company import CompanyRepository
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyDetail,
    CompanyList,
    Company as CompanySchema,
)

logger = logging.getLogger(__name__)


class CompanyService:
    """Service for company business logic"""

    def __init__(self, session: AsyncSession):
        self.repository = CompanyRepository(session)

    async def create_company(self, data: CompanyCreate, owner: User) -> CompanyDetail:
        """Create new company (any authenticated user can create)"""
        try:
            company = Company(
                name=data.name,
                description=data.description,
                owner_id=owner.id,
                is_visible=True
            )
            created_company = await self.repository.create(company)
            logger.info(f"Company created: {created_company.id} by user {owner.id}")
            return CompanyDetail.model_validate(created_company)
        except Exception as e:
            logger.error(f"Error creating company: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create company"
            )

    async def get_all_companies(self, skip: int = 0, limit: int = 100) -> CompanyList:
        """Get all visible companies with pagination"""
        try:
            companies = await self.repository.get_all(skip=skip, limit=limit, visible_only=True)
            total = await self.repository.count(visible_only=True)
            logger.info(f"Retrieved {len(companies)} companies (total: {total})")
            return CompanyList(
                companies=[CompanySchema.model_validate(company) for company in companies],
                total=total
            )
        except Exception as e:
            logger.error(f"Error getting companies: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve companies"
            )

    async def get_company_by_id(self, company_id: UUID) -> CompanyDetail:
        """Get company by ID (only visible companies or owner can see)"""
        try:
            company = await self.repository.get_by_id(company_id)
            if not company:
                logger.warning(f"Company not found: {company_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )
            logger.info(f"Retrieved company: {company_id}")
            return CompanyDetail.model_validate(company)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting company {company_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve company"
            )

    async def update_company(self, company_id: UUID, data: CompanyUpdate, current_user: User) -> CompanyDetail:
        """Update company (only owner can update)"""
        try:
            company = await self.repository.get_by_id(company_id)
            if not company:
                logger.warning(f"Company not found: {company_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )

            if company.owner_id != current_user.id:
                logger.warning(
                    f"User {current_user.id} attempted to update company {company_id} owned by {company.owner_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only company owner can update the company"
                )

            if data.name is not None:
                company.name = data.name
            if data.description is not None:
                company.description = data.description
            if data.is_visible is not None:
                company.is_visible = data.is_visible

            updated_company = await self.repository.update(company)
            logger.info(f"Company updated: {company_id} by owner {current_user.id}")
            return CompanyDetail.model_validate(updated_company)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating company {company_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update company"
            )

    async def delete_company(self, company_id: UUID, current_user: User) -> None:
        """Delete company (only owner can delete)"""
        try:
            company = await self.repository.get_by_id(company_id)
            if not company:
                logger.warning(f"Company not found: {company_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )

            if company.owner_id != current_user.id:
                logger.warning(
                    f"User {current_user.id} attempted to delete company {company_id} owned by {company.owner_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only company owner can delete the company"
                )

            await self.repository.delete(company)
            logger.info(f"Company deleted: {company_id} by owner {current_user.id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting company {company_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete company"
            )
