"""Pydantic models for position source data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PositionSourceBase(BaseModel):
    """Base model for position source data.

    Attributes:
        input_srid: Input spatial reference system identifier.
        input_timezone: Input timezone string.
        channels: Number of channels.
        start_time: Start timestamp.
        end_time: End timestamp.
        sample_rate: Sample rate in Hz.
        smoothing: Smoothing parameter.
        offset_x: X offset value.
        offset_y: Y offset value.
        offset_across_track: Across-track offset value.
        offset_along_track: Along-track offset value.
        offset_time: Time offset value.
    """

    input_srid: str
    input_timezone: str
    channels: int
    start_time: datetime
    end_time: datetime
    sample_rate: float | None = None
    smoothing: float | None = None
    offset_x: float | None = None
    offset_y: float | None = None
    offset_across_track: float | None = None
    offset_along_track: float | None = None
    offset_time: float | None = None


class PositionSourceCreate(PositionSourceBase):
    """Model for creating position source data.

    Attributes:
        device_id: Foreign key reference to Device.
        source_id: Foreign key reference to Source.
    """

    device_id: UUID
    source_id: UUID


class PositionSourceUpdate(PositionSourceBase):
    """Model for updating position source data.

    Attributes:
        input_srid: Input spatial reference system identifier.
        input_timezone: Input timezone string.
        channels: Number of channels.
        start_time: Start timestamp.
        end_time: End timestamp.
        sample_rate: Sample rate in Hz.
        smoothing: Smoothing parameter.
        offset_x: X offset value.
        offset_y: Y offset value.
        offset_across_track: Across-track offset value.
        offset_along_track: Along-track offset value.
        offset_time: Time offset value.
    """


class PositionSource(PositionSourceBase):
    """Model for position source data with database fields.

    Attributes:
        position_source_id: Unique identifier for the position source.
        device_id: Foreign key reference to Device.
        source_id: Foreign key reference to Source.
    """

    position_source_id: UUID
    device_id: UUID
    source_id: UUID

    model_config = ConfigDict(from_attributes=True)
