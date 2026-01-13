"""Pydantic models for raw layback data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RawLaybackBase(BaseModel):
    """Base model for raw layback data.

    Attributes:
        channel: Channel identifier.
        time: Timestamp of the layback measurement.
        value: Layback value in JSON format.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    channel: int | None = None
    time: datetime
    value: dict
    quality: float | None = None
    qc_flags: dict | None = None


class RawLaybackCreate(RawLaybackBase):
    """Model for creating raw layback data.

    Attributes:
        layback_source_id: Foreign key reference to LaybackSource.
    """

    layback_source_id: UUID


class RawLaybackUpdate(BaseModel):
    """Model for updating raw layback data.

    Attributes:
        channel: Channel identifier.
        time: Timestamp of the layback measurement.
        value: Layback value in JSON format.
        quality: Quality metric.
        qc_flags: Quality control flags in JSON format.
    """

    channel: int | None = None
    time: datetime | None = None
    value: dict | None = None
    quality: float | None = None
    qc_flags: dict | None = None


class RawLayback(RawLaybackBase):
    """Model for raw layback data with database fields.

    Attributes:
        raw_layback_id: Unique identifier for the raw layback.
        layback_source_id: Foreign key reference to LaybackSource.
    """

    raw_layback_id: UUID
    layback_source_id: UUID

    model_config = ConfigDict(from_attributes=True)
