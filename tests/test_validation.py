"""
Tests for user validation - users can only edit/delete their own profiles
"""
import pytest


def test_user_self_update_schema_only_allows_username_and_password():
    """Test UserSelfUpdateRequest schema only accepts username and password"""
    from app.schemas.user import UserSelfUpdateRequest

    valid_request = UserSelfUpdateRequest(username="newuser", password="newpass123")
    assert valid_request.username == "newuser"
    assert valid_request.password == "newpass123"

    assert not hasattr(valid_request, 'email')
    assert not hasattr(valid_request, 'is_active')


def test_user_service_has_validation_methods():
    """Test that UserService has update_self and delete_self methods"""
    from app.services.user import UserService

    assert hasattr(UserService, 'update_self')
    assert hasattr(UserService, 'delete_self')
    assert callable(getattr(UserService, 'update_self'))
    assert callable(getattr(UserService, 'delete_self'))


def test_validation_endpoints_are_registered():
    """Test that /users/me endpoints exist"""
    from app.api.routes.users import router

    routes = [route.path for route in router.routes]

    assert "/users/me" in routes

    me_routes = [route for route in router.routes if route.path == "/users/me"]

    assert len(me_routes) == 3

    all_methods = set()
    for route in me_routes:
        all_methods.update(route.methods)

    assert "GET" in all_methods
    assert "PUT" in all_methods
    assert "DELETE" in all_methods
