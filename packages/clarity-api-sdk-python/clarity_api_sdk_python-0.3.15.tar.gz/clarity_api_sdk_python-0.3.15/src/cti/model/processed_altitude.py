"""Pydantic models for processed altitude data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProcessedAltitudeBase(BaseModel):
    """Base model for processed altitude data.

    Attributes:
        channel: Channel identifier.
        time: Timestamp of the altitude measurement.
        altitude: Altitude value.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    channel: int
    time: datetime
    altitude: float
    quality: float | None = None
    qc_flags: dict


class ProcessedAltitudeCreate(ProcessedAltitudeBase):
    """Model for creating processed altitude data.

    Attributes:
        altitude_source_id: Foreign key reference to AltitudeSource.
    """

    altitude_source_id: UUID


class ProcessedAltitudeUpdate(ProcessedAltitudeBase):
    """Model for updating processed altitude data."""


class ProcessedAltitude(ProcessedAltitudeBase):
    """Model for processed altitude data with database fields.

    Attributes:
        processed_altitude_id: Unique identifier for the processed altitude.
        altitude_source_id: Foreign key reference to AltitudeSource.
    """

    processed_altitude_id: UUID
    altitude_source_id: UUID

    model_config = ConfigDict(from_attributes=True)
