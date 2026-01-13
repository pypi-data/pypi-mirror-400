"""Pydantic models for processed position data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProcessedPositionBase(BaseModel):
    """Base model for processed position data.

    Attributes:
        channel: Channel identifier.
        time: Timestamp of the position measurement.
        ship_x: Ship X coordinate.
        ship_y: Ship Y coordinate.
        fish_x: Fish X coordinate.
        fish_y: Fish Y coordinate.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    channel: int
    time: datetime
    ship_x: float | None = None
    ship_y: float | None = None
    fish_x: float
    fish_y: float
    quality: float | None = None
    qc_flags: dict


class ProcessedPositionCreate(ProcessedPositionBase):
    """Model for creating processed position data.

    Attributes:
        position_source_id: Foreign key reference to PositionSource.
    """

    position_source_id: UUID


class ProcessedPositionUpdate(BaseModel):
    """Model for updating processed position data.

    Attributes:
        channel: Channel identifier.
        time: Timestamp of the position measurement.
        ship_x: Ship X coordinate.
        ship_y: Ship Y coordinate.
        fish_x: Fish X coordinate.
        fish_y: Fish Y coordinate.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    channel: int | None = None
    time: datetime | None = None
    ship_x: float | None = None
    ship_y: float | None = None
    fish_x: float | None = None
    fish_y: float | None = None
    quality: float | None = None
    qc_flags: dict | None = None


class ProcessedPosition(ProcessedPositionBase):
    """Model for processed position data with database fields.

    Attributes:
        processed_position_id: Unique identifier for the processed position.
        position_source_id: Foreign key reference to PositionSource.
    """

    processed_position_id: UUID
    position_source_id: UUID

    model_config = ConfigDict(from_attributes=True)
