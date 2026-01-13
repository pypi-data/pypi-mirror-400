"""Pydantic models for projection option configuration."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectionOptionBase(BaseModel):
    """Base model for projection option configuration.

    Attributes:
        name: Name of the projection option.
        description: Description of the projection option.
    """

    name: str | None = None
    description: str | None = None


class ProjectionOptionCreate(ProjectionOptionBase):
    """Model for creating projection option data."""


class ProjectionOptionUpdate(ProjectionOptionBase):
    """Model for updating projection option data.

    Attributes:
        name: Name of the projection option.
        description: Description of the projection option.
    """


class ProjectionOption(ProjectionOptionBase):
    """Model for projection option configuration with database fields.

    Attributes:
        projection_option_id: Unique identifier for the projection option.
    """

    projection_option_id: UUID

    model_config = ConfigDict(from_attributes=True)
