from app.services.company_action import CompanyActionService
from app.schemas.company_action import (
    InvitationCreate,
    InvitationResponse,
    InvitationList,
    RequestResponse,
    RequestList,
    MemberResponse,
    MemberList
)


def test_company_action_service_methods_exist():
    """Test that CompanyActionService has all required methods"""
    assert hasattr(CompanyActionService, 'create_invitation')
    assert hasattr(CompanyActionService, 'cancel_invitation')
    assert hasattr(CompanyActionService, 'get_company_invitations')
    assert hasattr(CompanyActionService, 'get_user_invitations')
    assert hasattr(CompanyActionService, 'accept_invitation')
    assert hasattr(CompanyActionService, 'decline_invitation')
    assert hasattr(CompanyActionService, 'create_request')
    assert hasattr(CompanyActionService, 'cancel_request')
    assert hasattr(CompanyActionService, 'get_company_requests')
    assert hasattr(CompanyActionService, 'get_user_requests')
    assert hasattr(CompanyActionService, 'accept_request')
    assert hasattr(CompanyActionService, 'decline_request')
    assert hasattr(CompanyActionService, 'get_company_members')
    assert hasattr(CompanyActionService, 'remove_member')
    assert hasattr(CompanyActionService, 'leave_company')


def test_action_schemas_exist():
    """Test that action schemas are properly defined"""
    assert InvitationCreate is not None
    assert InvitationResponse is not None
    assert InvitationList is not None
    assert RequestResponse is not None
    assert RequestList is not None
    assert MemberResponse is not None
    assert MemberList is not None
