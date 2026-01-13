"""Pydantic models for processed attitude data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProcessedAttitudeBase(BaseModel):
    """Base model for processed attitude data.

    Attributes:
        channel: Channel identifier.
        time: Timestamp of the attitude measurement.
        grid_heading: Grid heading value.
        pitch: Pitch value.
        roll: Roll value.
        heave: Heave value.
        grid_course: Grid course value.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    channel: int
    time: datetime
    grid_heading: float
    pitch: float | None = None
    roll: float | None = None
    heave: float | None = None
    grid_course: float | None = None
    quality: float | None = None
    qc_flags: dict | None = None


class ProcessedAttitudeCreate(ProcessedAttitudeBase):
    """Model for creating processed attitude data.

    Attributes:
        attitude_source_id: Foreign key reference to AttitudeSource.
    """

    attitude_source_id: UUID


class ProcessedAttitudeUpdate(ProcessedAttitudeBase):
    """Model for updating processed attitude data."""


class ProcessedAttitude(ProcessedAttitudeBase):
    """Model for processed attitude data with database fields.

    Attributes:
        processed_attitude_id: Unique identifier for the processed attitude.
        attitude_source_id: Foreign key reference to AttitudeSource.
    """

    processed_attitude_id: UUID
    attitude_source_id: UUID

    model_config = ConfigDict(from_attributes=True)
