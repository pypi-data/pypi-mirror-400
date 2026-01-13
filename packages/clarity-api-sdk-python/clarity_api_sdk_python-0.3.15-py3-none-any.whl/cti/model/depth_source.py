"""Pydantic models for depth source data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DepthSourceBase(BaseModel):
    """Base model for depth source data.

    Attributes:
        input_timezone: Input timezone string.
        channels: Number of channels.
        start_time: Start timestamp.
        end_time: End timestamp.
        records: Number of records.
        sample_rate: Sample rate in Hz.
        smoothing: Smoothing parameter.
        offset_z: Z-axis offset.
        offset_time: Time offset.
    """

    input_timezone: str
    channels: int
    start_time: datetime
    end_time: datetime
    records: int | None = None
    sample_rate: float | None = None
    smoothing: float | None = None
    offset_z: float | None = None
    offset_time: float | None = None


class DepthSourceCreate(DepthSourceBase):
    """Model for creating depth source data.

    Attributes:
        device_id: Foreign key reference to Device.
        source_id: Foreign key reference to Source.
    """

    device_id: UUID
    source_id: UUID


class DepthSourceUpdate(BaseModel):
    """Model for updating depth source data.

    Attributes:
        input_timezone: Input timezone string.
        channels: Number of channels.
        start_time: Start timestamp.
        end_time: End timestamp.
        records: Number of records.
        sample_rate: Sample rate in Hz.
        smoothing: Smoothing parameter.
        offset_z: Z-axis offset.
        offset_time: Time offset.
    """

    input_timezone: str | None = None
    channels: int | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    records: int | None = None
    sample_rate: float | None = None
    smoothing: float | None = None
    offset_z: float | None = None
    offset_time: float | None = None


class DepthSource(DepthSourceBase):
    """Model for depth source data with database fields.

    Attributes:
        depth_source_id: Unique identifier for the depth source.
        device_id: Foreign key reference to Device.
        source_id: Foreign key reference to Source.
    """

    depth_source_id: UUID
    device_id: UUID
    source_id: UUID

    model_config = ConfigDict(from_attributes=True)
