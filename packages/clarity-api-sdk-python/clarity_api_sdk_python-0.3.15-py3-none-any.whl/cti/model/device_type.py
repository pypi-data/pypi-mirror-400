"""Pydantic models for device type data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DeviceTypeBase(BaseModel):
    """Base model for device type data.

    Attributes:
        name: Device type name.
        description: Device type description.
    """

    name: str
    description: str | None = None


class DeviceTypeCreate(DeviceTypeBase):
    """Model for creating device type data.

    Attributes:
        updated_by: User who created the device type.
    """


class DeviceTypeUpdate(DeviceTypeBase):
    """Model for updating device type data.

    Attributes:
        name: Device type name.
        description: Device type description.
        updated_by: User who updated the device type.
    """


class DeviceType(DeviceTypeBase):
    """Model for device type data with database fields.

    Attributes:
        device_type_id: Unique identifier for the device type.
        updated_by: User who last updated the device type.
        updated_date: Date when the device type was last updated.
        created_date: Date when the device type was created.
    """

    device_type_id: UUID
    updated_by: str
    updated_date: datetime
    created_date: datetime

    model_config = ConfigDict(from_attributes=True)


class DeviceTypes(BaseModel):
    """Model for a collection of device type."""

    device_types: list[DeviceType]
