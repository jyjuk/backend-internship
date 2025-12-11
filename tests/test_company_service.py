import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from app.services.company import CompanyService
from app.repositories.company import CompanyRepository
from app.models.user import User
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


@pytest.mark.asyncio
class TestCompanyService:
    """Tests for CompanyService"""

    async def test_create_company_success(self):
        """Test successful company creation"""
        mock_session = AsyncMock()
        owner_id = uuid4()

        mock_owner = User(
            id=owner_id,
            email="owner@test.com",
            username="owner",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        company_data = CompanyCreate(
            name="Test Company",
            description="Test Description"
        )

        created_company = Company(
            id=uuid4(),
            name="Test Company",
            description="Test Description",
            owner_id=owner_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = created_company

            service = CompanyService(mock_session)
            result = await service.create_company(company_data, mock_owner)

            assert result.name == "Test Company"
            assert result.description == "Test Description"
            mock_create.assert_called_once()

    async def test_get_all_companies_success(self):
        """Test getting all visible companies with pagination"""
        mock_session = AsyncMock()

        mock_companies = [
            Company(
                id=uuid4(),
                name="Company 1",
                owner_id=uuid4(),
                is_visible=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            ),
            Company(
                id=uuid4(),
                name="Company 2",
                owner_id=uuid4(),
                is_visible=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        ]

        with patch.object(CompanyRepository, 'get_all_visible', new_callable=AsyncMock) as mock_get_all:
            with patch.object(CompanyRepository, 'count_visible', new_callable=AsyncMock) as mock_count:
                mock_get_all.return_value = mock_companies
                mock_count.return_value = 2

                service = CompanyService(mock_session)
                result = await service.get_all_companies(skip=0, limit=100)

                assert result.total == 2
                assert len(result.companies) == 2
                assert result.companies[0].name == "Company 1"

    async def test_get_company_by_id_success(self):
        """Test getting company by ID"""
        mock_session = AsyncMock()
        company_id = uuid4()

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=uuid4(),
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_company

            service = CompanyService(mock_session)
            result = await service.get_company_by_id(company_id)

            assert result.id == company_id
            assert result.name == "Test Company"

    async def test_get_company_by_id_not_found(self):
        """Test get company fails when company doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            service = CompanyService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.get_company_by_id(company_id)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Company not found"

    async def test_update_company_success_by_owner(self):
        """Test owner successfully updates company"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()

        mock_owner = User(
            id=owner_id,
            email="owner@test.com",
            username="owner",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_company = Company(
            id=company_id,
            name="Old Name",
            description="Old Description",
            owner_id=owner_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        update_data = CompanyUpdate(
            name="New Name",
            description="New Description"
        )

        updated_company = Company(
            id=company_id,
            name="New Name",
            description="New Description",
            owner_id=owner_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            with patch.object(CompanyRepository, 'update', new_callable=AsyncMock) as mock_update:
                mock_get.return_value = mock_company
                mock_update.return_value = updated_company

                service = CompanyService(mock_session)
                result = await service.update_company(company_id, update_data, mock_owner)

                assert result.name == "New Name"
                assert result.description == "New Description"

    async def test_update_company_forbidden_not_owner(self):
        """Test non-owner cannot update company"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        other_user_id = uuid4()

        mock_other_user = User(
            id=other_user_id,
            email="other@test.com",
            username="other",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=owner_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        update_data = CompanyUpdate(name="New Name")

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_company

            service = CompanyService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.update_company(company_id, update_data, mock_other_user)

            assert exc_info.value.status_code == 403
            assert exc_info.value.detail == "Only company owner can update the company"

    async def test_update_company_not_found(self):
        """Test update fails when company doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()

        mock_user = User(
            id=uuid4(),
            email="user@test.com",
            username="user",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        update_data = CompanyUpdate(name="New Name")

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            service = CompanyService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.update_company(company_id, update_data, mock_user)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Company not found"

    async def test_delete_company_success_by_owner(self):
        """Test owner successfully deletes company"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()

        mock_owner = User(
            id=owner_id,
            email="owner@test.com",
            username="owner",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=owner_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            with patch.object(CompanyRepository, 'delete', new_callable=AsyncMock) as mock_delete:
                mock_get.return_value = mock_company

                service = CompanyService(mock_session)
                await service.delete_company(company_id, mock_owner)

                mock_delete.assert_called_once_with(mock_company)

    async def test_delete_company_forbidden_not_owner(self):
        """Test non-owner cannot delete company"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        other_user_id = uuid4()

        mock_other_user = User(
            id=other_user_id,
            email="other@test.com",
            username="other",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=owner_id,
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_company

            service = CompanyService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.delete_company(company_id, mock_other_user)

            assert exc_info.value.status_code == 403
            assert exc_info.value.detail == "Only company owner can delete the company"

    async def test_delete_company_not_found(self):
        """Test delete fails when company doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()

        mock_user = User(
            id=uuid4(),
            email="user@test.com",
            username="user",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            service = CompanyService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.delete_company(company_id, mock_user)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Company not found"
