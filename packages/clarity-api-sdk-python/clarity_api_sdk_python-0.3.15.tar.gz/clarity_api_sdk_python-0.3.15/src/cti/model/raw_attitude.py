"""Pydantic models for raw attitude data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RawAttitudeBase(BaseModel):
    """Base model for raw attitude data.

    Attributes:
        time: Timestamp of the attitude measurement.
        channel: Channel identifier.
        true_heading: True heading value.
        true_heading_offset: True heading offset value.
        meridian_angle: Meridian angle value.
        pitch: Pitch value.
        roll: Roll value.
        heave: Heave value.
        true_course: True course value.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    time: datetime
    channel: int
    true_heading: float
    true_heading_offset: float | None = None
    meridian_angle: float
    pitch: float | None = None
    roll: float | None = None
    heave: float | None = None
    true_course: float | None = None
    quality: float | None = None
    qc_flags: dict | None = None


class RawAttitudeCreate(RawAttitudeBase):
    """Model for creating raw attitude data.

    Attributes:
        attitude_source_id: Foreign key reference to AttitudeSource.
    """

    attitude_source_id: UUID


class RawAttitudeUpdate(RawAttitudeBase):
    """Model for updating raw attitude data.

    Attributes:
        time: Timestamp of the attitude measurement.
        channel: Channel identifier.
        true_heading: True heading value.
        true_heading_offset: True heading offset value.
        meridian_angle: Meridian angle value.
        pitch: Pitch value.
        roll: Roll value.
        heave: Heave value.
        true_course: True course value.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """


class RawAttitude(RawAttitudeBase):
    """Model for raw attitude data with database fields.

    Attributes:
        raw_attitude_id: Unique identifier for the raw attitude.
        attitude_source_id: Foreign key reference to AttitudeSource.
    """

    raw_attitude_id: UUID
    attitude_source_id: UUID

    model_config = ConfigDict(from_attributes=True)
