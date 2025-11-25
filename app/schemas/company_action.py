from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class InvitationCreate(BaseModel):
    """Schema for creating invitation"""
    invited_user_id: UUID = Field(..., description="User ID to invite")


class InvitationResponse(BaseModel):
    """Schema invitation response"""
    id: UUID
    company_id: UUID
    invited_user_id: UUID
    invited_by_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvitationList(BaseModel):
    """List of invitations"""
    invitations: list[InvitationResponse]
    total: int


class RequestCreate(BaseModel):
    """Schema for creating membership request"""
    pass


class RequestResponse(BaseModel):
    """Request response schema"""
    id: UUID
    company_id: UUID
    user_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RequestList(BaseModel):
    """List of requests"""
    requests: list[RequestResponse]
    total: int


class MemberResponse(BaseModel):
    """Company member response"""
    id: UUID
    user_id: UUID
    company_id: UUID
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemberList(BaseModel):
    """List of company members"""
    members: list[MemberResponse]
    total: int
