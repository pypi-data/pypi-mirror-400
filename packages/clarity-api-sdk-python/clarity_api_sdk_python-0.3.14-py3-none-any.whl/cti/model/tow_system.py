"""Pydantic models for tow system configuration."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TowSystemBase(BaseModel):
    """Base model for tow system configuration.

    Attributes:
        sensor_device_id: Foreign key reference to the sensor Device.
        sheave_device_id: Foreign key reference to the sheave Device.
    """

    sensor_device_id: UUID
    sheave_device_id: UUID


class TowSystemCreate(TowSystemBase):
    """Model for creating tow system configuration.

    Attributes:
        sensor_device_id: Foreign key reference to the sensor Device.
        sheave_device_id: Foreign key reference to the sheave Device.
    """


class TowSystemUpdate(TowSystemBase):
    """Model for updating tow system configuration.

    Attributes:
        sensor_device_id: Foreign key reference to the sensor Device.
        sheave_device_id: Foreign key reference to the sheave Device.
    """


class TowSystem(TowSystemBase):
    """Model for tow system configuration with database fields.

    Attributes:
        tow_system_id: Unique identifier for the tow system.
        sensor_device_id: Foreign key reference to the sensor Device.
        sheave_device_id: Foreign key reference to the sheave Device.
    """

    tow_system_id: UUID

    model_config = ConfigDict(from_attributes=True)
