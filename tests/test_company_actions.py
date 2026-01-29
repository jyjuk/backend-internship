from app.services.company_invitation_service import CompanyInvitationService
from app.services.company_request_service import CompanyRequestService
from app.services.company_member_service import CompanyMemberService
from app.schemas.company_action import (
    InvitationCreate, InvitationResponse, InvitationList,
    RequestResponse, RequestList, MemberResponse, MemberList
)


def test_company_invitation_service_methods_exist():
    """Test that CompanyInvitationService has all required methods"""
    assert hasattr(CompanyInvitationService, 'create_invitation')
    assert hasattr(CompanyInvitationService, 'cancel_invitation')
    assert hasattr(CompanyInvitationService, 'get_company_invitations')
    assert hasattr(CompanyInvitationService, 'get_user_invitations')
    assert hasattr(CompanyInvitationService, 'accept_invitation')
    assert hasattr(CompanyInvitationService, 'decline_invitation')


def test_company_request_service_methods_exist():
    """Test that CompanyRequestService has all required methods"""
    assert hasattr(CompanyRequestService, 'create_request')
    assert hasattr(CompanyRequestService, 'cancel_request')
    assert hasattr(CompanyRequestService, 'get_company_requests')
    assert hasattr(CompanyRequestService, 'get_user_requests')
    assert hasattr(CompanyRequestService, 'accept_request')
    assert hasattr(CompanyRequestService, 'decline_request')


def test_company_member_service_methods_exist():
    """Test that CompanyMemberService has all required methods"""
    assert hasattr(CompanyMemberService, 'get_company_members')
    assert hasattr(CompanyMemberService, 'remove_member')
    assert hasattr(CompanyMemberService, 'leave_company')


def test_action_schemas_exist():
    """Test that action schemas are properly defined"""
    assert InvitationCreate is not None
    assert InvitationResponse is not None
    assert InvitationList is not None
    assert RequestResponse is not None
    assert RequestList is not None
    assert MemberResponse is not None
    assert MemberList is not None
