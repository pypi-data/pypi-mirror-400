"""Pydantic models for platform type data."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlatformTypeBase(BaseModel):
    """Base model for platform type data.

    Attributes:
        name: Platform type name.
        description: Platform type description.
    """

    name: str
    description: str | None = None


class PlatformTypeCreate(PlatformTypeBase):
    """Model for creating platform type data.

    Attributes:
        name: Platform type name.
        description: Platform type description.
    """


class PlatformTypeUpdate(PlatformTypeBase):
    """Model for updating platform type data.

    Attributes:
        name: Platform type name.
        description: Platform type description.
    """


class PlatformType(PlatformTypeBase):
    """Model for platform type data with database fields.

    Attributes:
        platform_type_id: Unique identifier for the platform type.
    """

    platform_type_id: UUID

    model_config = ConfigDict(from_attributes=True)


class PlatformTypes(BaseModel):
    """Model for a collection of platform types."""

    platform_types: list[PlatformType]
