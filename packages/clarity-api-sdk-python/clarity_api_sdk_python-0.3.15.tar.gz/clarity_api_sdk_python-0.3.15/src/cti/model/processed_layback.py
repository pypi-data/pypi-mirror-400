"""Pydantic models for processed layback data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProcessedLaybackBase(BaseModel):
    """Base model for processed layback data.

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
    qc_flags: dict


class ProcessedLaybackCreate(ProcessedLaybackBase):
    """Model for creating processed layback data.

    Attributes:
        layback_source_id: Foreign key reference to LaybackSource.
    """

    layback_source_id: UUID


class ProcessedLaybackUpdate(BaseModel):
    """Model for updating processed layback data.

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


class ProcessedLayback(ProcessedLaybackBase):
    """Model for processed layback data with database fields.

    Attributes:
        processed_layback_id: Unique identifier for the processed layback.
        layback_source_id: Foreign key reference to LaybackSource.
    """

    processed_layback_id: UUID
    layback_source_id: UUID

    model_config = ConfigDict(from_attributes=True)
