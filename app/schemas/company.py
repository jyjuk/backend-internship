from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class CompanyBase(BaseModel):
    """Base company schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Company name")
    description: Optional[str] = Field(None, description="Company description")


class CompanyCreate(CompanyBase):
    """Schema for creating a company"""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Company name")
    description: Optional[str] = Field(None, description="Company description")
    is_visible: Optional[bool] = Field(None, description="Company visibility")


class Company(CompanyBase):
    """Company response schema"""
    id: UUID
    is_visible: bool
    owner_id: UUID

    model_config = ConfigDict(from_attributes=True)


class CompanyDetail(Company):
    """Detail company response with timestamps"""
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyList(BaseModel):
    """List of companies with pagination"""
    companies: list[Company]
    total: int

    model_config = ConfigDict(from_attributes=True)
