import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from app.services.company_invitation_service import CompanyInvitationService
from app.repositories.company import CompanyRepository
from app.repositories.company_member import CompanyMemberRepository
from app.repositories.company_invitation import CompanyInvitationRepository
from app.models.user import User
from app.models.company import Company
from app.models.company_member import CompanyMember
from app.models.company_invitation import CompanyInvitation, InvitationStatus
from app.schemas.company_action import InvitationCreate


@pytest.mark.asyncio
class TestCompanyInvitationService:
    """Tests for CompanyInvitationService"""

    async def test_create_invitation_success(self):
        """Test owner successfully creates invitation"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        invited_user_id = uuid4()

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

        invitation_data = InvitationCreate(invited_user_id=invited_user_id)

        created_invitation = CompanyInvitation(
            id=uuid4(),
            company_id=company_id,
            invited_user_id=invited_user_id,
            invited_by_id=owner_id,
            status=InvitationStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                with patch.object(CompanyInvitationRepository, 'get_pending_invitation',
                                  new_callable=AsyncMock) as mock_get_pending:
                    with patch.object(CompanyInvitationRepository, 'create', new_callable=AsyncMock) as mock_create:
                        mock_get_company.return_value = mock_company
                        mock_get_member.return_value = None
                        mock_get_pending.return_value = None
                        mock_create.return_value = created_invitation

                        service = CompanyInvitationService(mock_session)
                        result = await service.create_invitation(company_id, invitation_data, mock_owner)

                        assert result.invited_user_id == invited_user_id
                        assert result.status == InvitationStatus.PENDING
                        mock_create.assert_called_once()

    async def test_create_invitation_user_already_member(self):
        """Test create invitation fails when user is already a member"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        invited_user_id = uuid4()

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
            user_id=invited_user_id,
            company_id=company_id,
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        invitation_data = InvitationCreate(invited_user_id=invited_user_id)

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                mock_get_company.return_value = mock_company
                mock_get_member.return_value = mock_member

                service = CompanyInvitationService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.create_invitation(company_id, invitation_data, mock_owner)

                assert exc_info.value.status_code == 400
                assert exc_info.value.detail == "User is already a member"

    async def test_create_invitation_already_sent(self):
        """Test create invitation fails when invitation already exists"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        invited_user_id = uuid4()

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

        existing_invitation = CompanyInvitation(
            id=uuid4(),
            company_id=company_id,
            invited_user_id=invited_user_id,
            invited_by_id=owner_id,
            status=InvitationStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        invitation_data = InvitationCreate(invited_user_id=invited_user_id)

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                with patch.object(CompanyInvitationRepository, 'get_pending_invitation',
                                  new_callable=AsyncMock) as mock_get_pending:
                    mock_get_company.return_value = mock_company
                    mock_get_member.return_value = None
                    mock_get_pending.return_value = existing_invitation

                    service = CompanyInvitationService(mock_session)

                    with pytest.raises(HTTPException) as exc_info:
                        await service.create_invitation(company_id, invitation_data, mock_owner)

                    assert exc_info.value.status_code == 400
                    assert exc_info.value.detail == "Invitation already sent"

    async def test_cancel_invitation_success(self):
        """Test owner successfully cancels invitation"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        invitation_id = uuid4()

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

        mock_invitation = CompanyInvitation(
            id=invitation_id,
            company_id=company_id,
            invited_user_id=uuid4(),
            invited_by_id=owner_id,
            status=InvitationStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyInvitationRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_invitation:
                with patch.object(CompanyInvitationRepository, 'update', new_callable=AsyncMock) as mock_update:
                    mock_get_company.return_value = mock_company
                    mock_get_invitation.return_value = mock_invitation

                    service = CompanyInvitationService(mock_session)
                    await service.cancel_invitation(company_id, invitation_id, mock_owner)

                    assert mock_invitation.status == InvitationStatus.CANCELLED
                    mock_update.assert_called_once()

    async def test_cancel_invitation_not_pending(self):
        """Test cancel fails when invitation is not pending"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        invitation_id = uuid4()

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

        mock_invitation = CompanyInvitation(
            id=invitation_id,
            company_id=company_id,
            invited_user_id=uuid4(),
            invited_by_id=owner_id,
            status=InvitationStatus.ACCEPTED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyInvitationRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_invitation:
                mock_get_company.return_value = mock_company
                mock_get_invitation.return_value = mock_invitation

                service = CompanyInvitationService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.cancel_invitation(company_id, invitation_id, mock_owner)

                assert exc_info.value.status_code == 400
                assert exc_info.value.detail == "Can only cancel pending invitations"

    async def test_get_company_invitations_success(self):
        """Test owner gets list of company invitations"""
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

        mock_invitations = [
            CompanyInvitation(
                id=uuid4(),
                company_id=company_id,
                invited_user_id=uuid4(),
                invited_by_id=owner_id,
                status=InvitationStatus.PENDING,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        ]

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyInvitationRepository, 'get_company_invitations',
                              new_callable=AsyncMock) as mock_get_invitations:
                with patch.object(CompanyInvitationRepository, 'count_company_invitations',
                                  new_callable=AsyncMock) as mock_count:
                    mock_get_company.return_value = mock_company
                    mock_get_invitations.return_value = mock_invitations
                    mock_count.return_value = 1

                    service = CompanyInvitationService(mock_session)
                    result = await service.get_company_invitations(company_id, mock_owner, skip=0, limit=100)

                    assert result.total == 1
                    assert len(result.invitations) == 1

    async def test_get_user_invitations_success(self):
        """Test user gets list of received invitations"""
        mock_session = AsyncMock()
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

        mock_invitations = [
            CompanyInvitation(
                id=uuid4(),
                company_id=uuid4(),
                invited_user_id=user_id,
                invited_by_id=uuid4(),
                status=InvitationStatus.PENDING,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        ]

        with patch.object(CompanyInvitationRepository, 'get_user_invitations',
                          new_callable=AsyncMock) as mock_get_invitations:
            with patch.object(CompanyInvitationRepository, 'count_user_invitations',
                              new_callable=AsyncMock) as mock_count:
                mock_get_invitations.return_value = mock_invitations
                mock_count.return_value = 1

                service = CompanyInvitationService(mock_session)
                result = await service.get_user_invitations(mock_user, skip=0, limit=100)

                assert result.total == 1
                assert len(result.invitations) == 1

    async def test_accept_invitation_success(self):
        """Test user successfully accepts invitation"""
        mock_session = AsyncMock()
        invitation_id = uuid4()
        user_id = uuid4()
        company_id = uuid4()

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

        mock_invitation = CompanyInvitation(
            id=invitation_id,
            company_id=company_id,
            invited_user_id=user_id,
            invited_by_id=uuid4(),
            status=InvitationStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyInvitationRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_invitation:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                with patch.object(CompanyMemberRepository, 'create', new_callable=AsyncMock) as mock_create_member:
                    with patch.object(CompanyInvitationRepository, 'update',
                                      new_callable=AsyncMock) as mock_update_invitation:
                        mock_get_invitation.return_value = mock_invitation
                        mock_get_member.return_value = None

                        service = CompanyInvitationService(mock_session)
                        await service.accept_invitation(invitation_id, mock_user)

                        assert mock_invitation.status == InvitationStatus.ACCEPTED
                        mock_create_member.assert_called_once()
                        mock_update_invitation.assert_called_once()

    async def test_accept_invitation_not_pending(self):
        """Test accept fails when invitation is not pending"""
        mock_session = AsyncMock()
        invitation_id = uuid4()
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

        mock_invitation = CompanyInvitation(
            id=invitation_id,
            company_id=uuid4(),
            invited_user_id=user_id,
            invited_by_id=uuid4(),
            status=InvitationStatus.DECLINED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyInvitationRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_invitation:
            mock_get_invitation.return_value = mock_invitation

            service = CompanyInvitationService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.accept_invitation(invitation_id, mock_user)

            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Invitation is not pending"

    async def test_accept_invitation_not_found(self):
        """Test accept fails when invitation doesn't exist"""
        mock_session = AsyncMock()
        invitation_id = uuid4()

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

        with patch.object(CompanyInvitationRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_invitation:
            mock_get_invitation.return_value = None

            service = CompanyInvitationService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.accept_invitation(invitation_id, mock_user)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Invitation not found"

    async def test_decline_invitation_success(self):
        """Test user successfully declines invitation"""
        mock_session = AsyncMock()
        invitation_id = uuid4()
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

        mock_invitation = CompanyInvitation(
            id=invitation_id,
            company_id=uuid4(),
            invited_user_id=user_id,
            invited_by_id=uuid4(),
            status=InvitationStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyInvitationRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_invitation:
            with patch.object(CompanyInvitationRepository, 'update', new_callable=AsyncMock) as mock_update:
                mock_get_invitation.return_value = mock_invitation

                service = CompanyInvitationService(mock_session)
                await service.decline_invitation(invitation_id, mock_user)

                assert mock_invitation.status == InvitationStatus.DECLINED
                mock_update.assert_called_once()

    async def test_decline_invitation_not_pending(self):
        """Test decline fails when invitation is not pending"""
        mock_session = AsyncMock()
        invitation_id = uuid4()
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

        mock_invitation = CompanyInvitation(
            id=invitation_id,
            company_id=uuid4(),
            invited_user_id=user_id,
            invited_by_id=uuid4(),
            status=InvitationStatus.ACCEPTED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyInvitationRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_invitation:
            mock_get_invitation.return_value = mock_invitation

            service = CompanyInvitationService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.decline_invitation(invitation_id, mock_user)

            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Invitation is not pending"
