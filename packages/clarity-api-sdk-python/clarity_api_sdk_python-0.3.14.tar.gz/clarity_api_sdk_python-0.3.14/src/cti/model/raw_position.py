"""Pydantic models for raw position data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RawPositionBase(BaseModel):
    """Base model for raw position data.

    Attributes:
        time: Timestamp of the position measurement.
        channel: Channel identifier.
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.
        speed: Speed value.
        course: Course value.
        altitude: Altitude value.
        hdop: Horizontal dilution of precision.
        vdop: Vertical dilution of precision.
        tdop: Time dilution of precision.
        pdop: Position dilution of precision.
        gdop: Geometric dilution of precision.
        position_type: Type of position measurement.
        num_satellites: Number of satellites used.
        sensor_status: Sensor status in JSON format.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    time: datetime
    channel: int
    latitude: float
    longitude: float
    speed: float | None = None
    course: float | None = None
    altitude: float | None = None
    hdop: float | None = None
    vdop: float | None = None
    tdop: float | None = None
    pdop: float | None = None
    gdop: float | None = None
    position_type: str | None = None
    num_satellites: int | None = None
    sensor_status: dict | None = None
    quality: float | None = None
    qc_flags: dict | None = None


class RawPositionCreate(RawPositionBase):
    """Model for creating raw position data.

    Attributes:
        position_source_id: Foreign key reference to PositionSource.
    """

    position_source_id: UUID


class RawPositionUpdate(BaseModel):
    """Model for updating raw position data.

    Attributes:
        time: Timestamp of the position measurement.
        channel: Channel identifier.
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.
        speed: Speed value.
        course: Course value.
        altitude: Altitude value.
        hdop: Horizontal dilution of precision.
        vdop: Vertical dilution of precision.
        tdop: Time dilution of precision.
        pdop: Position dilution of precision.
        gdop: Geometric dilution of precision.
        position_type: Type of position measurement.
        num_satellites: Number of satellites used.
        sensor_status: Sensor status in JSON format.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    time: datetime | None = None
    channel: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    speed: float | None = None
    course: float | None = None
    altitude: float | None = None
    hdop: float | None = None
    vdop: float | None = None
    tdop: float | None = None
    pdop: float | None = None
    gdop: float | None = None
    position_type: str | None = None
    num_satellites: int | None = None
    sensor_status: dict | None = None
    quality: float | None = None
    qc_flags: dict | None = None


class RawPosition(RawPositionBase):
    """Model for raw position data with database fields.

    Attributes:
        raw_position_id: Unique identifier for the raw position.
        position_source_id: Foreign key reference to PositionSource.
    """

    raw_position_id: UUID
    position_source_id: UUID

    model_config = ConfigDict(from_attributes=True)
