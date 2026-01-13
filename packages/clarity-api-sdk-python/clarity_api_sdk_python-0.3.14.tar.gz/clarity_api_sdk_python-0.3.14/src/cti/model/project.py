"""Project model."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectBase(BaseModel):
    """Base project model.

    Attributes:
        project_name: Name of the project.
        project_description: Description of the project.
        updated_by: User who last updated the project.
    """

    project_name: str
    project_description: str


class ProjectCreate(ProjectBase):
    """Schema for creating a project.

    Attributes:
        organization_id: Organization ID for the project.
    """

    organization_id: UUID


class ProjectUpdate(ProjectBase):
    """Schema for updating a project."""


class Project(ProjectBase):
    """Project model with database fields.

    Attributes:
        project_id: Unique identifier for the project.
        organization_id: Organization ID for the project.
        created_date: Date when the project was created.
        updated_date: Date when the project was last updated.
    """

    project_id: UUID
    organization_id: UUID
    created_date: datetime
    updated_date: datetime
    updated_by: str

    model_config = ConfigDict(from_attributes=True)
