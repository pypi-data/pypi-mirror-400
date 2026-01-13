"""Pydantic models for raw sidescan ping data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RawSidescanPingBase(BaseModel):
    """Base model for raw sidescan ping data.

    Attributes:
        time: Timestamp of the ping.
        ping_number: Ping sequence number.
        channel: Channel identifier.
        max_two_way_time: Maximum two-way travel time.
        altitude: Altitude measurement.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    time: datetime
    channel: int
    max_two_way_time: float
    altitude: float | None = None
    quality: float | None = None
    qc_flags: dict


class RawSidescanPingCreate(RawSidescanPingBase):
    """Model for creating raw sidescan ping data.

    Attributes:
        sidescan_ping_source_id: Foreign key reference to SidescanPingSource.
    """

    sidescan_ping_source_id: UUID
    ping_number_id: UUID


class RawSidescanPingUpdate(RawSidescanPingBase):
    """Model for updating raw sidescan ping data.

    Attributes:
        time: Timestamp of the ping.
        ping_number: Ping sequence number.
        channel: Channel identifier.
        max_two_way_time: Maximum two-way travel time.
        altitude: Altitude measurement.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """


class RawSidescanPing(RawSidescanPingBase):
    """Model for raw sidescan ping data with database fields.

    Attributes:
        raw_sidescan_pings_id: Unique identifier for the raw sidescan ping.
        sidescan_ping_source_id: Foreign key reference to SidescanPingSource.
    """

    raw_sidescan_pings_id: UUID
    sidescan_ping_source_id: UUID
    ping_number_id: UUID

    model_config = ConfigDict(from_attributes=True)
