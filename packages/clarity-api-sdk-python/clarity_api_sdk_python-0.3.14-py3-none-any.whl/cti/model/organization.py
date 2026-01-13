"""Organization model"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationBase(BaseModel):
    """Base schema for Organization.

    Attributes:
        name: Name of the organization.
        updated_by: User who updated the organization.
    """

    name: str


class OrganizationCreate(OrganizationBase):
    """Schema for creating an Organization."""


class OrganizationUpdate(OrganizationBase):
    """Schema for updating an Organization."""


class Organization(OrganizationBase):
    """Schema for Organization response.

    Attributes:
        organization_id: Unique identifier for the organization.
        updated_date: Date when the organization was updated.
        created_date: Date when the organization was created.
    """

    organization_id: UUID
    updated_date: datetime
    created_date: datetime
    updated_by: str | None = None

    model_config = ConfigDict(from_attributes=True)
