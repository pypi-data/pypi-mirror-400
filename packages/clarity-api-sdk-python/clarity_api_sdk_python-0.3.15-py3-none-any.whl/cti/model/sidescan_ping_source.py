"""Pydantic models for sidescan ping source data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SidescanPingSourceBase(BaseModel):
    """Base model for sidescan ping source data.

    Attributes:
        channels: Number of channels.
        input_timezone: Input timezone name.
        start_time: Start time of the data.
        end_time: End time of the data.
        sound_velocity: Sound velocity value.
        frequency: Frequency value.
        sample_rate: Sample rate value.
        ping_rate: Ping rate value.
        max_two_way_time: Maximum two-way time value.
        start_display_record: Start display record index.
        stop_display_record: Stop display record index.
        draw_order: Draw order value.
        zarr_path: Path to zarr file.
        zarr_group: Zarr group identifier.
    """

    channels: int
    input_timezone: str
    start_time: datetime
    end_time: datetime
    sound_velocity: float
    frequency: float | None = None
    sample_rate: float | None = None
    ping_rate: float | None = None
    max_two_way_time: float
    start_display_record: int | None = None
    stop_display_record: int | None = None
    draw_order: int | None = None
    zarr_path: str | None = None
    zarr_group: str | None = None


class SidescanPingSourceCreate(SidescanPingSourceBase):
    """Model for creating sidescan ping source data.

    Attributes:
        device_id: Foreign key reference to Device.
        source_id: Foreign key reference to Source.
    """

    device_id: UUID
    source_id: UUID


class SidescanPingSourceUpdate(BaseModel):
    """Model for updating sidescan ping source data.

    Attributes:
        channels: Number of channels.
        input_timezone: Input timezone name.
        start_time: Start time of the data.
        end_time: End time of the data.
        sound_velocity: Sound velocity value.
        frequency: Frequency value.
        sample_rate: Sample rate value.
        ping_rate: Ping rate value.
        max_two_way_time: Maximum two-way time value.
        start_display_record: Start display record index.
        stop_display_record: Stop display record index.
        draw_order: Draw order value.
        zarr_path: Path to zarr file.
        zarr_group: Zarr group identifier.
    """

    channels: int | None = None
    input_timezone: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    sound_velocity: float | None = None
    frequency: float | None = None
    sample_rate: float | None = None
    ping_rate: float | None = None
    max_two_way_time: float | None = None
    start_display_record: int | None = None
    stop_display_record: int | None = None
    draw_order: int | None = None
    zarr_path: str | None = None
    zarr_group: str | None = None


class SidescanPingSource(SidescanPingSourceBase):
    """Model for sidescan ping source data with database fields.

    Attributes:
        sidescan_ping_source_id: Unique identifier for the sidescan ping source.
        device_id: Foreign key reference to Device.
        source_id: Foreign key reference to Source.
    """

    sidescan_ping_source_id: UUID
    device_id: UUID
    source_id: UUID

    model_config = ConfigDict(from_attributes=True)
