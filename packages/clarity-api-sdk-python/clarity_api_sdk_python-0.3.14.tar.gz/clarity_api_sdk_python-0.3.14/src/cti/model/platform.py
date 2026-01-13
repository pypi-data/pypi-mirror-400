"""Pydantic models for platform data."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlatformBase(BaseModel):
    """Base model for platform data.

    Attributes:
        name: Platform name.
        description: Platform description.
    """

    name: str
    description: str | None = None


class PlatformCreate(PlatformBase):
    """Model for creating platform data.

    Attributes:
        survey_id: Foreign key reference to Survey.
        platform_type_id: Foreign key reference to PlatformType.
    """

    survey_id: UUID
    platform_type_id: UUID


class PlatformUpdate(PlatformBase):
    """Model for updating platform data."""


class Platform(PlatformBase):
    """Model for platform data with database fields.

    Attributes:
        platform_id: Unique identifier for the platform.
        survey_id: Foreign key reference to Survey.
        platform_type_id: Foreign key reference to PlatformType.
    """

    platform_id: UUID
    survey_id: UUID
    platform_type_id: UUID

    model_config = ConfigDict(from_attributes=True)


class Platforms(BaseModel):
    """Model for a collection of platforms."""

    platforms: list[Platform]
