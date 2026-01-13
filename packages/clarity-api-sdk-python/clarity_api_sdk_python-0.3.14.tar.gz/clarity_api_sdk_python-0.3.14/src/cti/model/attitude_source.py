"""Pydantic models for attitude source data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AttitudeSourceBase(BaseModel):
    """Base model for attitude source data.

    Attributes:
        input_timezone: Input timezone string.
        channels: Number of channels.
        start_time: Start timestamp.
        end_time: End timestamp.
        sample_rate: Sample rate in Hz.
        projection_option: Foreign key reference to ProjectionOption.
        apply_pitch: Whether to apply pitch correction.
        offset_roll: Roll offset value.
        offset_pitch: Pitch offset value.
        offset_heading: Heading offset value.
        offset_time: Time offset value.
    """

    input_timezone: str
    channels: int
    start_time: datetime
    end_time: datetime
    sample_rate: float | None = None
    projection_option: UUID
    apply_pitch: bool | None = None
    offset_roll: float | None = None
    offset_pitch: float | None = None
    offset_heading: float | None = None
    offset_time: float | None = None


class AttitudeSourceCreate(AttitudeSourceBase):
    """Model for creating attitude source data.

    Attributes:
        device_id: Foreign key reference to Device.
        source_id: Foreign key reference to Source.
    """

    device_id: UUID
    source_id: UUID


class AttitudeSourceUpdate(BaseModel):
    """Model for updating attitude source data.

    Attributes:
        input_timezone: Input timezone string.
        channels: Number of channels.
        start_time: Start timestamp.
        end_time: End timestamp.
        sample_rate: Sample rate in Hz.
        projection_option: Foreign key reference to ProjectionOption.
        apply_pitch: Whether to apply pitch correction.
        offset_roll: Roll offset value.
        offset_pitch: Pitch offset value.
        offset_heading: Heading offset value.
        offset_time: Time offset value.
    """

    input_timezone: str | None = None
    channels: int | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    sample_rate: float | None = None
    projection_option: UUID | None = None
    apply_pitch: bool | None = None
    offset_roll: float | None = None
    offset_pitch: float | None = None
    offset_heading: float | None = None
    offset_time: float | None = None


class AttitudeSource(AttitudeSourceBase):
    """Model for attitude source data with database fields.

    Attributes:
        attitude_source_id: Unique identifier for the attitude source.
        device_id: Foreign key reference to Device.
        source_id: Foreign key reference to Source.
    """

    attitude_source_id: UUID
    device_id: UUID
    source_id: UUID

    model_config = ConfigDict(from_attributes=True)
