"""Pydantic models for device data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DeviceBase(BaseModel):
    """Base model for device data.

    Attributes:
        name: Device name.
        channels: Number of channels.
        offset_x: X-axis offset.
        offset_y: Y-axis offset.
        offset_z: Z-axis offset.
        offset_heading: Heading offset.
        offset_pitch: Pitch offset.
        offset_roll: Roll offset.
        latency: Device latency.
        is_towed: Whether the device is towed.
    """

    name: str
    channels: int
    offset_x: float
    offset_y: float
    offset_z: float
    offset_heading: float
    offset_pitch: float
    offset_roll: float
    latency: float
    is_towed: bool


class DeviceCreate(DeviceBase):
    """Model for creating device data.

    Attributes:
        platform_id: Foreign key reference to Platform.
        device_type_id: Foreign key reference to DeviceType.
    """

    platform_id: UUID
    device_type_id: UUID


class DeviceUpdate(DeviceBase):
    """Model for updating device data.

    Attributes:
        name: Device name.
        channels: Number of channels.
        offset_x: X-axis offset.
        offset_y: Y-axis offset.
        offset_z: Z-axis offset.
        offset_heading: Heading offset.
        offset_pitch: Pitch offset.
        offset_roll: Roll offset.
        latency: Device latency.
        is_towed: Whether the device is towed.
        updated_by: User who updated the device.
    """


class Device(DeviceBase):
    """Model for device data with database fields.

    Attributes:
        device_id: Unique identifier for the device.
        platform_id: Foreign key reference to Platform.
        device_type_id: Foreign key reference to DeviceType.
        updated_by: User who last updated the device.
        updated_date: Date when the device was last updated.
        created_date: Date when the device was created.
    """

    device_id: UUID
    platform_id: UUID
    device_type_id: UUID
    updated_by: str
    updated_date: datetime
    created_date: datetime

    model_config = ConfigDict(from_attributes=True)


class Devices(BaseModel):
    """Model for a collection of devices."""

    devices: list[Device]
