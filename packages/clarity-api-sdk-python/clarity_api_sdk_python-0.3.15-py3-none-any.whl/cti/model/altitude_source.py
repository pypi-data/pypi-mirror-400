"""Pydantic models for altitude source data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AltitudeSourceBase(BaseModel):
    """Base model for altitude source data.

    Attributes:
        input_timezone: Input timezone string.
        start_time: Start timestamp.
        end_time: End timestamp.
        channels: Number of channels.
    """

    input_timezone: str
    start_time: datetime
    end_time: datetime
    channels: int


class AltitudeSourceCreate(AltitudeSourceBase):
    """Model for creating altitude source data.

    Attributes:
        device_id: Foreign key reference to Device.
        source_id: Foreign key reference to Source.
    """

    device_id: UUID
    source_id: UUID


class AltitudeSourceUpdate(BaseModel):
    """Model for updating altitude source data.

    Attributes:
        input_timezone: Input timezone string.
        start_time: Start timestamp.
        end_time: End timestamp.
        channels: Number of channels.
    """

    input_timezone: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    channels: int | None = None


class AltitudeSource(AltitudeSourceBase):
    """Model for altitude source data with database fields.

    Attributes:
        altitude_source_id: Unique identifier for the altitude source.
        device_id: Foreign key reference to Device.
        source_id: Foreign key reference to Source.
    """

    altitude_source_id: UUID
    device_id: UUID
    source_id: UUID

    model_config = ConfigDict(from_attributes=True)
