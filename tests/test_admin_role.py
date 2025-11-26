from app.services.company_member_service import CompanyMemberService
from app.repositories.company_member import CompanyMemberRepository


def test_company_member_service_has_admin_methods():
    """Test that CompanyMemberService has admin management methods"""
    assert hasattr(CompanyMemberService, 'promote_to_admin')
    assert hasattr(CompanyMemberService, 'demote_from_admin')
    assert hasattr(CompanyMemberService, 'get_company_admins')


def test_company_member_repository_has_admin_methods():
    """Test that CompanyMemberRepository has admin query methods"""
    assert hasattr(CompanyMemberRepository, 'get_company_admins')
    assert hasattr(CompanyMemberRepository, 'count_company_admins')


def test_member_response_has_is_admin_field():
    """Test that MemberResponse schema includes is_admin field"""
    from app.schemas.company_action import MemberResponse
    from pydantic import BaseModel

    assert 'is_admin' in MemberResponse.model_fields

    field_info = MemberResponse.model_fields['is_admin']
    assert field_info.annotation == bool
