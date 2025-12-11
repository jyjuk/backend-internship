import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from app.services.company_member_service import CompanyMemberService
from app.repositories.company import CompanyRepository
from app.repositories.company_member import CompanyMemberRepository
from app.models.user import User
from app.models.company import Company
from app.models.company_member import CompanyMember


@pytest.mark.asyncio
class TestCompanyMemberService:
    """Tests for CompanyMemberService"""

    async def test_check_company_owner_success(self):
        """Test that company owner has access"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()

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

            service = CompanyMemberService(mock_session)
            await service._check_company_owner(company_id, owner_id)

            mock_get.assert_called_once_with(company_id)

    async def test_check_company_owner_company_not_found(self):
        """Test that 404 raised when company doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()
        user_id = uuid4()

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            service = CompanyMemberService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service._check_company_owner(company_id, user_id)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Company not found"

    async def test_check_company_owner_not_owner_forbidden(self):
        """Test that non-owner gets 403"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        other_user_id = uuid4()

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

            service = CompanyMemberService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service._check_company_owner(company_id, other_user_id)

            assert exc_info.value.status_code == 403
            assert exc_info.value.detail == "Only company owner can perform this action"

    async def test_get_company_members_success(self):
        """Test getting company members returns list"""
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

        mock_members = [
            CompanyMember(
                id=uuid4(),
                user_id=uuid4(),
                company_id=company_id,
                is_admin=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            ),
            CompanyMember(
                id=uuid4(),
                user_id=uuid4(),
                company_id=company_id,
                is_admin=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        ]

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_company_members',
                              new_callable=AsyncMock) as mock_get_members:
                with patch.object(CompanyMemberRepository, 'count_company_members',
                                  new_callable=AsyncMock) as mock_count:
                    mock_get_company.return_value = mock_company
                    mock_get_members.return_value = mock_members
                    mock_count.return_value = 2

                    service = CompanyMemberService(mock_session)
                    result = await service.get_company_members(company_id, skip=0, limit=100)

                    assert result.total == 2
                    assert len(result.members) == 2

    async def test_get_company_members_company_not_found(self):
        """Test get members fails when company doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            service = CompanyMemberService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.get_company_members(company_id)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Company not found"

    async def test_remove_member_success_by_owner(self):
        """Test owner successfully removes member"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        member_user_id = uuid4()

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

        mock_member = CompanyMember(
            id=uuid4(),
            user_id=member_user_id,
            company_id=company_id,
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                with patch.object(CompanyMemberRepository, 'delete', new_callable=AsyncMock) as mock_delete:
                    mock_get_company.return_value = mock_company
                    mock_get_member.return_value = mock_member

                    service = CompanyMemberService(mock_session)
                    await service.remove_member(company_id, member_user_id, mock_owner)

                    mock_delete.assert_called_once_with(mock_member)

    async def test_remove_member_forbidden_not_owner(self):
        """Test non-owner cannot remove member"""
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

            service = CompanyMemberService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.remove_member(company_id, uuid4(), mock_other_user)

            assert exc_info.value.status_code == 403

    async def test_remove_member_not_found(self):
        """Test remove fails when member doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        member_user_id = uuid4()

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

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                mock_get_company.return_value = mock_company
                mock_get_member.return_value = None

                service = CompanyMemberService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.remove_member(company_id, member_user_id, mock_owner)

                assert exc_info.value.status_code == 404
                assert exc_info.value.detail == "Member not found"

    async def test_leave_company_success(self):
        """Test user successfully leaves company"""
        mock_session = AsyncMock()
        company_id = uuid4()
        user_id = uuid4()

        mock_user = User(
            id=user_id,
            email="user@test.com",
            username="user",
            is_active=True,
            is_superuser=False,
            hashed_password="hashed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        mock_member = CompanyMember(
            id=uuid4(),
            user_id=user_id,
            company_id=company_id,
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                          new_callable=AsyncMock) as mock_get_member:
            with patch.object(CompanyMemberRepository, 'delete', new_callable=AsyncMock) as mock_delete:
                mock_get_member.return_value = mock_member

                service = CompanyMemberService(mock_session)
                await service.leave_company(company_id, mock_user)

                mock_delete.assert_called_once_with(mock_member)

    async def test_leave_company_not_member(self):
        """Test leave fails when user is not a member"""
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

        with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                          new_callable=AsyncMock) as mock_get_member:
            mock_get_member.return_value = None

            service = CompanyMemberService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.leave_company(company_id, mock_user)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "You are not a member of this company"

    async def test_promote_to_admin_success(self):
        """Test owner successfully promotes member to admin"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        member_user_id = uuid4()

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

        mock_member = CompanyMember(
            id=uuid4(),
            user_id=member_user_id,
            company_id=company_id,
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                with patch.object(CompanyMemberRepository, 'update', new_callable=AsyncMock) as mock_update:
                    mock_get_company.return_value = mock_company
                    mock_get_member.return_value = mock_member

                    service = CompanyMemberService(mock_session)
                    await service.promote_to_admin(company_id, member_user_id, mock_owner)

                    assert mock_member.is_admin == True
                    mock_update.assert_called_once_with(mock_member)

    async def test_promote_to_admin_already_admin(self):
        """Test promote fails when member is already admin"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        member_user_id = uuid4()

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

        mock_member = CompanyMember(
            id=uuid4(),
            user_id=member_user_id,
            company_id=company_id,
            is_admin=True,  # Already admin
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                mock_get_company.return_value = mock_company
                mock_get_member.return_value = mock_member

                service = CompanyMemberService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.promote_to_admin(company_id, member_user_id, mock_owner)

                assert exc_info.value.status_code == 400
                assert exc_info.value.detail == "User is already an admin"

    async def test_promote_to_admin_member_not_found(self):
        """Test promote fails when member doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        member_user_id = uuid4()

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

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                mock_get_company.return_value = mock_company
                mock_get_member.return_value = None

                service = CompanyMemberService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.promote_to_admin(company_id, member_user_id, mock_owner)

                assert exc_info.value.status_code == 404
                assert exc_info.value.detail == "Member not found"

    async def test_demote_from_admin_success(self):
        """Test owner successfully demotes admin to regular member"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        member_user_id = uuid4()

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

        mock_member = CompanyMember(
            id=uuid4(),
            user_id=member_user_id,
            company_id=company_id,
            is_admin=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                with patch.object(CompanyMemberRepository, 'update', new_callable=AsyncMock) as mock_update:
                    mock_get_company.return_value = mock_company
                    mock_get_member.return_value = mock_member

                    service = CompanyMemberService(mock_session)
                    await service.demote_from_admin(company_id, member_user_id, mock_owner)

                    assert mock_member.is_admin == False
                    mock_update.assert_called_once_with(mock_member)

    async def test_demote_from_admin_not_admin(self):
        """Test demote fails when member is not an admin"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        member_user_id = uuid4()

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

        mock_member = CompanyMember(
            id=uuid4(),
            user_id=member_user_id,
            company_id=company_id,
            is_admin=False,  # Not admin
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                mock_get_company.return_value = mock_company
                mock_get_member.return_value = mock_member

                service = CompanyMemberService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.demote_from_admin(company_id, member_user_id, mock_owner)

                assert exc_info.value.status_code == 400
                assert exc_info.value.detail == "User is not an admin"

    async def test_demote_from_admin_member_not_found(self):
        """Test demote fails when member doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        member_user_id = uuid4()

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

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                mock_get_company.return_value = mock_company
                mock_get_member.return_value = None

                service = CompanyMemberService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.demote_from_admin(company_id, member_user_id, mock_owner)

                assert exc_info.value.status_code == 404
                assert exc_info.value.detail == "Member not found"

    async def test_get_company_admins_success(self):
        """Test getting company admins returns list"""
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

        mock_admins = [
            CompanyMember(
                id=uuid4(),
                user_id=uuid4(),
                company_id=company_id,
                is_admin=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        ]

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_company_admins', new_callable=AsyncMock) as mock_get_admins:
                with patch.object(CompanyMemberRepository, 'count_company_admins',
                                  new_callable=AsyncMock) as mock_count:
                    mock_get_company.return_value = mock_company
                    mock_get_admins.return_value = mock_admins
                    mock_count.return_value = 1

                    service = CompanyMemberService(mock_session)
                    result = await service.get_company_admins(company_id, skip=0, limit=100)

                    assert result.total == 1
                    assert len(result.members) == 1

    async def test_get_company_admins_company_not_found(self):
        """Test get admins fails when company doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            service = CompanyMemberService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.get_company_admins(company_id)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Company not found"
