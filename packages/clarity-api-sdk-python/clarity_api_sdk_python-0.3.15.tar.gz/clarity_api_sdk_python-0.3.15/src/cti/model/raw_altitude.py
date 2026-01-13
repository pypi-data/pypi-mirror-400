"""Pydantic models for raw altitude data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RawAltitudeBase(BaseModel):
    """Base model for raw altitude data.

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


class RawAltitudeCreate(RawAltitudeBase):
    """Model for creating raw altitude data.

    Attributes:
        altitude_source_id: Foreign key reference to AltitudeSource.
    """

    altitude_source_id: UUID


class RawAltitudeUpdate(BaseModel):
    """Model for updating raw altitude data.

    Attributes:
        channel: Channel identifier.
        time: Timestamp of the altitude measurement.
        altitude: Altitude value.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    channel: int | None = None
    time: datetime | None = None
    altitude: float | None = None
    quality: float | None = None
    qc_flags: dict | None = None


class RawAltitude(RawAltitudeBase):
    """Model for raw altitude data with database fields.

    Attributes:
        raw_altitude_id: Unique identifier for the raw altitude.
        altitude_source_id: Foreign key reference to AltitudeSource.
    """

    raw_altitude_id: UUID
    altitude_source_id: UUID

    model_config = ConfigDict(from_attributes=True)
