"""
Tests for company CRUD operations
"""
import pytest


def test_company_service_methods_exist():
    """Test that CompanyService has all required methods"""
    from app.services.company import CompanyService

    assert hasattr(CompanyService, 'create_company')
    assert hasattr(CompanyService, 'get_all_companies')
    assert hasattr(CompanyService, 'get_company_by_id')
    assert hasattr(CompanyService, 'update_company')
    assert hasattr(CompanyService, 'delete_company')

    assert callable(getattr(CompanyService, 'create_company'))
    assert callable(getattr(CompanyService, 'get_all_companies'))
    assert callable(getattr(CompanyService, 'get_company_by_id'))
    assert callable(getattr(CompanyService, 'update_company'))
    assert callable(getattr(CompanyService, 'delete_company'))


def test_company_schemas_exist():
    """Test that company schemas are defined"""
    from app.schemas.company import (
        CompanyCreate,
        CompanyUpdate,
        Company,
        CompanyDetail,
        CompanyList
    )

    create_data = CompanyCreate(name="Test Company", description="Test")
    assert create_data.name == "Test Company"
    assert create_data.description == "Test"

    update_data = CompanyUpdate(name="Updated")
    assert update_data.name == "Updated"
    assert update_data.description is None
    assert update_data.is_visible is None


def test_company_endpoints_are_registered():
    """Test that /companies endpoints exist"""
    from app.api.routes.companies import router

    routes = [route.path for route in router.routes]

    assert "/companies/" in routes
    assert "/companies/{company_id}" in routes

    # Check methods
    create_route = next(route for route in router.routes if route.path == "/companies/" and "POST" in route.methods)
    assert create_route is not None

    list_route = next(route for route in router.routes if route.path == "/companies/" and "GET" in route.methods)
    assert list_route is not None


def test_company_model_has_owner_relationship():
    """Test that Company model has owner relationship"""
    from app.models.company import Company

    assert hasattr(Company, 'owner')
    assert hasattr(Company, 'owner_id')
