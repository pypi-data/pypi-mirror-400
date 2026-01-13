"""Pydantic models for target data."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TargetBase(BaseModel):
    """Base model for target data.

    Attributes:
        name: Target name.
        description: Target description.
        target_x: X coordinate of the target.
        target_y: Y coordinate of the target.
        width: Target width.
        height: Target height.
        shadow: Target shadow.
    """

    name: str
    description: str
    target_x: float
    target_y: float
    width: float | None = None
    height: float | None = None
    shadow: float | None = None


class TargetCreate(TargetBase):
    """Model for creating target data.

    Attributes:
        processed_sidescan_ping_id: Foreign key reference to ProcessedSidescanPing.
    """

    processed_sidescan_ping_id: UUID


class TargetUpdate(TargetBase):
    """Model for updating target data."""


class Target(TargetBase):
    """Model for target data with database fields.

    Attributes:
        target_id: Unique identifier for the target.
        processed_sidescan_ping_id: Foreign key reference to ProcessedSidescanPing.
    """

    target_id: UUID
    processed_sidescan_ping_id: UUID

    model_config = ConfigDict(from_attributes=True)
