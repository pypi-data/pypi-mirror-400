"""Pydantic schemas for Organization."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class OrganizationStatus(str, Enum):
    """Status of an organization."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class OrganizationCreate(BaseModel):
    """Schema for creating an organization."""

    name: str
    status: OrganizationStatus = OrganizationStatus.ACTIVE
    clerk_auth_org_id: str | None = None


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""

    name: str | None = None
    status: OrganizationStatus | None = None
    clerk_auth_org_id: str | None = None


class Organization(BaseModel):
    """Schema for organization response."""

    id: int
    name: str
    status: OrganizationStatus
    clerk_auth_org_id: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
