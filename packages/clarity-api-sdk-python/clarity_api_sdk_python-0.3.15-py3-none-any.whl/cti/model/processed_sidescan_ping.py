"""Pydantic models for processed sidescan ping data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProcessedSidescanPingBase(BaseModel):
    """Base model for processed sidescan ping data.

    Attributes:
        time: Timestamp of the ping.
        ping_number: Ping number identifier.
        channel: Channel number.
        max_two_way_time: Maximum two-way time value.
        altitude: Altitude value.
        beam_end_x: Beam end X coordinate.
        beam_end_y: Beam end Y coordinate.
        start_display_sample: Start display sample index.
        stop_display_sample: Stop display sample index.
        zarr_path: Path to zarr file.
        zarr_group: Zarr group identifier.
        quality: Quality value.
        qc_flags: Quality control flags in JSON format.
    """

    time: datetime
    ping_number: int
    channel: int
    max_two_way_time: float
    altitude: float | None = None
    beam_end_x: float | None = None
    beam_end_y: float | None = None
    start_display_sample: int | None = None
    stop_display_sample: int | None = None
    zarr_path: str | None = None
    zarr_group: str | None = None
    quality: float | None = None
    qc_flags: dict | None = None


class ProcessedSidescanPingCreate(ProcessedSidescanPingBase):
    """Model for creating processed sidescan ping data.

    Attributes:
        sidescan_ping_source_id: Foreign key reference to SidescanPingSource.
    """

    sidescan_ping_source_id: UUID


class ProcessedSidescanPingUpdate(ProcessedSidescanPingBase):
    """Model for updating processed sidescan ping data."""


class ProcessedSidescanPing(ProcessedSidescanPingBase):
    """Model for processed sidescan ping data with database fields.

    Attributes:
        processed_sidescan_ping_id: Unique identifier for the processed sidescan ping.
        sidescan_ping_source_id: Foreign key reference to SidescanPingSource.
    """

    processed_sidescan_ping_id: UUID
    sidescan_ping_source_id: UUID

    model_config = ConfigDict(from_attributes=True)
