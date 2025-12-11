import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from app.services.company_request_service import CompanyRequestService
from app.repositories.company import CompanyRepository
from app.repositories.company_member import CompanyMemberRepository
from app.repositories.company_request import CompanyRequestRepository
from app.models.user import User
from app.models.company import Company
from app.models.company_member import CompanyMember
from app.models.company_request import CompanyRequest, RequestStatus


@pytest.mark.asyncio
class TestCompanyRequestService:
    """Tests for CompanyRequestService"""

    async def test_create_request_success(self):
        """Test user successfully creates request to join company"""
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

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=uuid4(),
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        created_request = CompanyRequest(
            id=uuid4(),
            company_id=company_id,
            user_id=user_id,
            status=RequestStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                with patch.object(CompanyRequestRepository, 'get_pending_request',
                                  new_callable=AsyncMock) as mock_get_pending:
                    with patch.object(CompanyRequestRepository, 'create', new_callable=AsyncMock) as mock_create:
                        mock_get_company.return_value = mock_company
                        mock_get_member.return_value = None
                        mock_get_pending.return_value = None
                        mock_create.return_value = created_request

                        service = CompanyRequestService(mock_session)
                        result = await service.create_request(company_id, mock_user)

                        assert result.user_id == user_id
                        assert result.status == RequestStatus.PENDING
                        mock_create.assert_called_once()

    async def test_create_request_user_already_member(self):
        """Test create request fails when user is already a member"""
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

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=uuid4(),
            is_visible=True,
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

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                mock_get_company.return_value = mock_company
                mock_get_member.return_value = mock_member

                service = CompanyRequestService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.create_request(company_id, mock_user)

                assert exc_info.value.status_code == 400
                assert exc_info.value.detail == "User is already a member"

    async def test_create_request_already_sent(self):
        """Test create request fails when request already exists"""
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

        mock_company = Company(
            id=company_id,
            name="Test Company",
            owner_id=uuid4(),
            is_visible=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        existing_request = CompanyRequest(
            id=uuid4(),
            company_id=company_id,
            user_id=user_id,
            status=RequestStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                              new_callable=AsyncMock) as mock_get_member:
                with patch.object(CompanyRequestRepository, 'get_pending_request',
                                  new_callable=AsyncMock) as mock_get_pending:
                    mock_get_company.return_value = mock_company
                    mock_get_member.return_value = None
                    mock_get_pending.return_value = existing_request

                    service = CompanyRequestService(mock_session)

                    with pytest.raises(HTTPException) as exc_info:
                        await service.create_request(company_id, mock_user)

                    assert exc_info.value.status_code == 400
                    assert exc_info.value.detail == "Request already sent"

    async def test_cancel_request_success(self):
        """Test user successfully cancels their request"""
        mock_session = AsyncMock()
        company_id = uuid4()
        user_id = uuid4()
        request_id = uuid4()

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

        mock_request = CompanyRequest(
            id=request_id,
            company_id=company_id,
            user_id=user_id,
            status=RequestStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRequestRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_request:
            with patch.object(CompanyRequestRepository, 'update', new_callable=AsyncMock) as mock_update:
                mock_get_request.return_value = mock_request

                service = CompanyRequestService(mock_session)
                await service.cancel_request(company_id, request_id, mock_user)

                assert mock_request.status == RequestStatus.CANCELLED
                mock_update.assert_called_once()

    async def test_cancel_request_not_pending(self):
        """Test cancel fails when request is not pending"""
        mock_session = AsyncMock()
        company_id = uuid4()
        user_id = uuid4()
        request_id = uuid4()

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

        mock_request = CompanyRequest(
            id=request_id,
            company_id=company_id,
            user_id=user_id,
            status=RequestStatus.ACCEPTED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRequestRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_request:
            mock_get_request.return_value = mock_request

            service = CompanyRequestService(mock_session)

            with pytest.raises(HTTPException) as exc_info:
                await service.cancel_request(company_id, request_id, mock_user)

            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Can only cancel pending requests"

    async def test_get_company_requests_success(self):
        """Test owner gets list of company requests"""
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

        mock_requests = [
            CompanyRequest(
                id=uuid4(),
                company_id=company_id,
                user_id=uuid4(),
                status=RequestStatus.PENDING,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        ]

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyRequestRepository, 'get_company_requests',
                              new_callable=AsyncMock) as mock_get_requests:
                with patch.object(CompanyRequestRepository, 'count_company_requests',
                                  new_callable=AsyncMock) as mock_count:
                    mock_get_company.return_value = mock_company
                    mock_get_requests.return_value = mock_requests
                    mock_count.return_value = 1

                    service = CompanyRequestService(mock_session)
                    result = await service.get_company_requests(company_id, mock_owner, skip=0, limit=100)

                    assert result.total == 1
                    assert len(result.requests) == 1

    async def test_get_user_requests_success(self):
        """Test user gets list of their requests"""
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

        mock_requests = [
            CompanyRequest(
                id=uuid4(),
                company_id=uuid4(),
                user_id=user_id,
                status=RequestStatus.PENDING,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        ]

        with patch.object(CompanyRequestRepository, 'get_user_requests', new_callable=AsyncMock) as mock_get_requests:
            with patch.object(CompanyRequestRepository, 'count_user_requests', new_callable=AsyncMock) as mock_count:
                mock_get_requests.return_value = mock_requests
                mock_count.return_value = 1

                service = CompanyRequestService(mock_session)
                result = await service.get_user_requests(mock_user, skip=0, limit=100)

                assert result.total == 1
                assert len(result.requests) == 1

    async def test_accept_request_success(self):
        """Test owner successfully accepts request"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        user_id = uuid4()
        request_id = uuid4()

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

        mock_request = CompanyRequest(
            id=request_id,
            company_id=company_id,
            user_id=user_id,
            status=RequestStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyRequestRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_request:
                with patch.object(CompanyMemberRepository, 'get_by_user_and_company',
                                  new_callable=AsyncMock) as mock_get_member:
                    with patch.object(CompanyMemberRepository, 'create', new_callable=AsyncMock) as mock_create_member:
                        with patch.object(CompanyRequestRepository, 'update',
                                          new_callable=AsyncMock) as mock_update_request:
                            mock_get_company.return_value = mock_company
                            mock_get_request.return_value = mock_request
                            mock_get_member.return_value = None

                            service = CompanyRequestService(mock_session)
                            await service.accept_request(company_id, request_id, mock_owner)

                            assert mock_request.status == RequestStatus.ACCEPTED
                            mock_create_member.assert_called_once()
                            mock_update_request.assert_called_once()

    async def test_accept_request_not_pending(self):
        """Test accept fails when request is not pending"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        request_id = uuid4()

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

        mock_request = CompanyRequest(
            id=request_id,
            company_id=company_id,
            user_id=uuid4(),
            status=RequestStatus.DECLINED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyRequestRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_request:
                mock_get_company.return_value = mock_company
                mock_get_request.return_value = mock_request

                service = CompanyRequestService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.accept_request(company_id, request_id, mock_owner)

                assert exc_info.value.status_code == 400
                assert exc_info.value.detail == "Request is not pending"

    async def test_accept_request_not_found(self):
        """Test accept fails when request doesn't exist"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        request_id = uuid4()

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
            with patch.object(CompanyRequestRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_request:
                mock_get_company.return_value = mock_company
                mock_get_request.return_value = None

                service = CompanyRequestService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.accept_request(company_id, request_id, mock_owner)

                assert exc_info.value.status_code == 404
                assert exc_info.value.detail == "Request not found"

    async def test_decline_request_success(self):
        """Test owner successfully declines request"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        request_id = uuid4()

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

        mock_request = CompanyRequest(
            id=request_id,
            company_id=company_id,
            user_id=uuid4(),
            status=RequestStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyRequestRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_request:
                with patch.object(CompanyRequestRepository, 'update', new_callable=AsyncMock) as mock_update:
                    mock_get_company.return_value = mock_company
                    mock_get_request.return_value = mock_request

                    service = CompanyRequestService(mock_session)
                    await service.decline_request(company_id, request_id, mock_owner)

                    assert mock_request.status == RequestStatus.DECLINED
                    mock_update.assert_called_once()

    async def test_decline_request_not_pending(self):
        """Test decline fails when request is not pending"""
        mock_session = AsyncMock()
        company_id = uuid4()
        owner_id = uuid4()
        request_id = uuid4()

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

        mock_request = CompanyRequest(
            id=request_id,
            company_id=company_id,
            user_id=uuid4(),
            status=RequestStatus.ACCEPTED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(CompanyRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_company:
            with patch.object(CompanyRequestRepository, 'get_by_id', new_callable=AsyncMock) as mock_get_request:
                mock_get_company.return_value = mock_company
                mock_get_request.return_value = mock_request

                service = CompanyRequestService(mock_session)

                with pytest.raises(HTTPException) as exc_info:
                    await service.decline_request(company_id, request_id, mock_owner)

                assert exc_info.value.status_code == 400
                assert exc_info.value.detail == "Request is not pending"
