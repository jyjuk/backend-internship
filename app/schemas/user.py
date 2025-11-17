from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_serializer
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class SignUpRequest(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)


class SignInRequest(BaseModel):
    """Schema for login"""
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None


class UserDetail(UserBase):
    """Schema for detail user"""
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("id")
    def serializer_id(self, value: UUID) -> str:
        return str(value)


class User(UserBase):
    """Schema for simple user"""
    id: UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("id")
    def serialize_id(self, value:UUID) -> str:
        return str(value)


class UserList(BaseModel):
    """Schema for list of users"""
    users: list[User]
    total: int
